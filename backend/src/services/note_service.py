"""Business pipeline for note writes and relation generation.

The service coordinates validation, model inference, pgvector search through
repositories, relation decisions, and evidence persistence.
"""

from __future__ import annotations

from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.database import transaction
from src.data.evidence_repository import EvidenceRepository
from src.data.folder_repository import FolderRepository
from src.data.models import NoteRecord, RelationEvidenceInput, RelationSummary
from src.data.note_repository import NoteRepository
from src.data.relation_repository import RelationRepository
from src.services.relation_service import RelationService
from src.services.sentence_processor import SentenceProcessor


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

    def create_note(self, folder_id: UUID, sentence: str) -> NoteRecord:
        """Create a note and build relations against similar active notes."""
        sentence = self._validate_sentence(sentence)
        embedding = self.sentence_processor.embedding(sentence)

        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            note = self.note_repository.create_note(
                connection=connection,
                folder_id=folder_id,
                sentence=sentence,
                embedding=embedding,
            )
            self._rebuild_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                source_note=note,
                source_embedding=embedding,
            )
            return note

    def update_note(self, folder_id: UUID, note_id: UUID, sentence: str) -> NoteRecord:
        """Update a note and rebuild all active relations connected to it."""
        sentence = self._validate_sentence(sentence)
        embedding = self.sentence_processor.embedding(sentence)

        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            self.relation_repository.soft_delete_relations_for_note(
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
                raise ValueError("Note not found.")

            self._rebuild_relations_for_note(
                connection=connection,
                folder_id=folder_id,
                source_note=note,
                source_embedding=embedding,
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
                raise ValueError("Note not found.")

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
    ) -> None:
        """Find similar notes, classify relations, and store relation evidence."""
        candidates = self.note_repository.find_similar_notes(
            connection=connection,
            folder_id=folder_id,
            source_note_id=source_note.note_id,
            query_embedding=source_embedding,
            top_k=self.config.similarity_top_k,
            threshold=self.config.similarity_threshold,
        )

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
            relation = self.relation_repository.create_relation(
                connection=connection,
                folder_id=folder_id,
                note_id_1=source_note.note_id,
                note_id_2=candidate.note_id,
                relation_type=decision.relation_type,
                process_status="relation_confirmed",
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
                    llm_payload={
                        "note_1": source_note.sentence,
                        "note_2": candidate.sentence,
                        "similarity_score": candidate.similarity_score,
                        "NLI Lable": decision.nli_label,
                        "NLI Score": decision.nli_score,
                        "words_overlap": words_overlap,
                        "similar_world": similar_words,
                    },
                ),
            )

    def _validate_sentence(self, sentence: str) -> str:
        normalized = sentence.strip()
        if not normalized:
            raise ValueError("Sentence must not be empty.")
        return normalized

    def _ensure_folder_exists(self, connection, folder_id: UUID) -> None:
        folder = self.folder_repository.get_folder(
            connection=connection,
            folder_id=folder_id,
        )
        if folder is None:
            raise ValueError("Folder not found.")
