"""Business pipeline for note writes and relation generation.

The service coordinates validation, model inference, pgvector search through
repositories, relation decisions, and evidence persistence.
"""

from __future__ import annotations

import logging
from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.constants import (
    ERROR_FOLDER_NOT_FOUND,
    ERROR_NOTE_NOT_FOUND,
    ERROR_SENTENCE_EMPTY,
    PROCESS_STATUS_RELATION_CONFIRMED,
)
from src.core.database import transaction
from src.core.timing import Timer
from src.data.evidence_repository import EvidenceRepository
from src.data.folder_repository import FolderRepository
from src.data.models import NoteRecord, RelationEvidenceInput, RelationSummary
from src.data.note_repository import NoteRepository
from src.data.relation_repository import RelationRepository
from src.services.llm_payload import build_relation_llm_payload
from src.services.relation_service import RelationService
from src.services.sentence_processor import SentenceProcessor


logger = logging.getLogger(__name__)


class NoteService:
    """Coordinates note writes, embeddings, relation rebuilding, and reads."""

    def __init__(
        self,
        config: AppConfig | None = None,
        sentence_processor: SentenceProcessor | None = None,
        folder_repository: FolderRepository | None = None,
        note_repository: NoteRepository | None = None,
        relation_repository: RelationRepository | None = None,
        evidence_repository: EvidenceRepository | None = None,
    ) -> None:
        self.config = config or get_config()
        self._sentence_processor = sentence_processor
        self.folder_repository = folder_repository or FolderRepository()
        self.note_repository = note_repository or NoteRepository()
        self.relation_repository = relation_repository or RelationRepository()
        self.evidence_repository = evidence_repository or EvidenceRepository()
        self.relation_service = RelationService(
            similarity_threshold=self.config.similarity_threshold,
            threshold_scale=self.config.threshold_scale,
        )

    @property
    def sentence_processor(self) -> SentenceProcessor:
        """Load AI models lazily so read-only terminal actions stay lightweight."""
        if self._sentence_processor is None:
            self._sentence_processor = SentenceProcessor(
                embedding_model_name=self.config.embedding_model,
                nli_model_name=self.config.nli_model,
                embedding_dimension=self.config.embedding_dimension,
            )
        return self._sentence_processor

    def model_statuses(self) -> dict[str, str]:
        """Report loaded model state without triggering a lazy model load."""
        if self._sentence_processor is None:
            return {"embedding": "not_loaded", "nli": "not_loaded"}
        return self._sentence_processor.model_statuses()

    def create_note(self, folder_id: UUID, sentence: str) -> NoteRecord:
        """Create a note and build relations against similar active notes."""
        total_timer = Timer()
        sentence = self._validate_sentence(sentence)
        embedding_timer = Timer()
        embedding = self.sentence_processor.embedding(sentence)
        logger.info(
            "note_pipeline embedding operation=create_note folder_id=%s duration_ms=%s",
            folder_id,
            embedding_timer.elapsed_ms,
        )

        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            # Note writes and relation evidence are committed together so a saved
            # note never points at a half-built AI pipeline result.
            note = self.note_repository.create_note(
                connection=connection,
                folder_id=folder_id,
                sentence=sentence,
                embedding=embedding,
            )
            relation_count = self._rebuild_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                source_note=note,
                source_embedding=embedding,
            )
            self.folder_repository.touch_updated_at(
                connection=connection,
                folder_id=folder_id,
            )
            logger.info(
                "note_pipeline create_note folder_id=%s note_id=%s relations_created=%s duration_ms=%s",
                folder_id,
                note.note_id,
                relation_count,
                total_timer.elapsed_ms,
            )
            return note

    def update_note(self, folder_id: UUID, note_id: UUID, sentence: str) -> NoteRecord:
        """Update a note and rebuild all active relations connected to it."""
        total_timer = Timer()
        sentence = self._validate_sentence(sentence)
        embedding_timer = Timer()
        embedding = self.sentence_processor.embedding(sentence)
        logger.info(
            "note_pipeline embedding operation=update_note folder_id=%s note_id=%s duration_ms=%s",
            folder_id,
            note_id,
            embedding_timer.elapsed_ms,
        )

        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            # Updating a note invalidates the old relation evidence connected to
            # that note, so the active relation set is rebuilt from the new text.
            deleted_relations = self.relation_repository.soft_delete_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                note_id=note_id,
            )
            note = self.note_repository.update_note(
                connection=connection,
                folder_id=folder_id,
                note_id=note_id,
                sentence=sentence,
                embedding=embedding,
            )
            if note is None:
                raise ValueError(ERROR_NOTE_NOT_FOUND)

            relation_count = self._rebuild_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                source_note=note,
                source_embedding=embedding,
            )
            self.folder_repository.touch_updated_at(
                connection=connection,
                folder_id=folder_id,
            )
            logger.info(
                "note_pipeline update_note folder_id=%s note_id=%s relations_deleted=%s relations_created=%s duration_ms=%s",
                folder_id,
                note_id,
                deleted_relations,
                relation_count,
                total_timer.elapsed_ms,
            )
            return note

    def delete_note(self, folder_id: UUID, note_id: UUID) -> None:
        """Soft delete a note and all active relations connected to it."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            self.relation_repository.soft_delete_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                note_id=note_id,
            )
            deleted = self.note_repository.soft_delete_note(
                connection=connection,
                folder_id=folder_id,
                note_id=note_id,
            )
            if not deleted:
                raise ValueError(ERROR_NOTE_NOT_FOUND)
            self.folder_repository.touch_updated_at(
                connection=connection,
                folder_id=folder_id,
            )

    def get_note(self, folder_id: UUID, note_id: UUID) -> NoteRecord:
        """Return one active note from an active folder."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            note = self.note_repository.get_note(
                connection=connection,
                folder_id=folder_id,
                note_id=note_id,
            )
            if note is None:
                raise ValueError(ERROR_NOTE_NOT_FOUND)
            return note

    def list_notes(self, folder_id: UUID) -> list[NoteRecord]:
        """List active notes in an active folder."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            return self.note_repository.list_notes(
                connection=connection,
                folder_id=folder_id,
            )

    def list_relations(self, folder_id: UUID) -> list[RelationSummary]:
        """List active relations in an active folder."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            return self.relation_repository.list_relations(
                connection=connection,
                folder_id=folder_id,
            )

    def _rebuild_relations_for_note(
        self,
        connection,
        folder_id: UUID,
        source_note: NoteRecord,
        source_embedding: list[float],
    ) -> int:
        """Find similar notes, classify relations, and store relation evidence."""
        timer = Timer()
        candidates = self.note_repository.find_similar_notes(
            connection=connection,
            folder_id=folder_id,
            source_note_id=source_note.note_id,
            query_embedding=source_embedding,
            top_k=self.config.similarity_top_k,
            threshold=self.config.similarity_threshold,
        )

        created_count = 0
        for candidate in candidates:
            # NLI is direction-sensitive. The current direction follows the
            # discovery path: source note as premise, candidate as hypothesis.
            nli_result = self.sentence_processor.nli_similarity(
                source_note.sentence,
                candidate.sentence,
            )
            decision = self.relation_service.classify(
                similarity_score=candidate.similarity_score,
                nli_result=nli_result,
            )
            if decision is None:
                continue

            words_overlap = self.sentence_processor.word_overlap(
                source_note.sentence,
                candidate.sentence,
            )
            similar_words = self.sentence_processor.similar_words(
                source_note.sentence,
                candidate.sentence,
                threshold=self.config.similar_word_threshold,
            )
            # Relation rows store the confirmed relationship state; evidence rows
            # store model details and the frozen LLM payload used by Phase 3.
            relation = self.relation_repository.create_relation(
                connection=connection,
                folder_id=folder_id,
                note_id_1=source_note.note_id,
                note_id_2=candidate.note_id,
                relation_type=decision.relation_type,
                process_status=PROCESS_STATUS_RELATION_CONFIRMED,
            )
            self.evidence_repository.create_evidence(
                connection=connection,
                evidence=RelationEvidenceInput(
                    relation_id=relation.relation_id,
                    similarity_score=candidate.similarity_score,
                    nli_score=decision.nli_score,
                    nli_label=decision.nli_label,
                    words_overlap=words_overlap,
                    similar_words=similar_words,
                    llm_payload=build_relation_llm_payload(
                        note_1=source_note.sentence,
                        note_2=candidate.sentence,
                    ),
                ),
            )
            created_count += 1

        logger.info(
            "note_pipeline rebuild_relations folder_id=%s note_id=%s candidates=%s relations_created=%s duration_ms=%s",
            folder_id,
            source_note.note_id,
            len(candidates),
            created_count,
            timer.elapsed_ms,
        )
        return created_count

    def _validate_sentence(self, sentence: str) -> str:
        normalized = sentence.strip()
        if not normalized:
            raise ValueError(ERROR_SENTENCE_EMPTY)
        return normalized

    def _ensure_folder_exists(self, connection, folder_id: UUID) -> None:
        folder = self.folder_repository.get_folder(
            connection=connection,
            folder_id=folder_id,
        )
        if folder is None:
            raise ValueError(ERROR_FOLDER_NOT_FOUND)
