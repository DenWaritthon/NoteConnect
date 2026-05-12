"""Business workflow for relation explanations."""

from __future__ import annotations

import logging
from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.constants import (
    ERROR_EXPLANATION_NOT_FOUND,
    ERROR_FOLDER_NOT_FOUND,
    ERROR_RELATION_EVIDENCE_NOT_FOUND,
    PROCESS_STATUS_ADD_EXPLANATION,
)
from src.core.database import transaction
from src.core.timing import Timer
from src.data.evidence_repository import EvidenceRepository
from src.data.folder_repository import FolderRepository
from src.data.models import RelationExplanationRecord
from src.data.relation_repository import RelationRepository
from src.services.explanation_generator import ExplanationGenerator


logger = logging.getLogger(__name__)


class ExplanationService:
    """Reads or creates explanations from stored relation evidence payloads."""

    def __init__(
        self,
        explanation_generator: ExplanationGenerator,
        config: AppConfig | None = None,
        folder_repository: FolderRepository | None = None,
        relation_repository: RelationRepository | None = None,
        evidence_repository: EvidenceRepository | None = None,
    ) -> None:
        self.config = config or get_config()
        self.explanation_generator = explanation_generator
        self.folder_repository = folder_repository or FolderRepository()
        self.relation_repository = relation_repository or RelationRepository()
        self.evidence_repository = evidence_repository or EvidenceRepository()

    def get_explanation(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationExplanationRecord:
        """Return an existing explanation without generating one."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            # GET is intentionally read-only. Missing explanation returns 404
            # instead of triggering generation, so clients control write timing.
            evidence = self.evidence_repository.get_latest_explanation_evidence(
                connection=connection,
                folder_id=folder_id,
                relation_id=relation_id,
            )
            if evidence is None:
                raise ValueError(ERROR_RELATION_EVIDENCE_NOT_FOUND)
            if not evidence.explanation:
                raise ValueError(ERROR_EXPLANATION_NOT_FOUND)
            return RelationExplanationRecord(
                relation_id=evidence.relation_id,
                explanation=evidence.explanation,
            )

    def create_explanation(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> tuple[RelationExplanationRecord, bool]:
        """Return an existing explanation or generate and store a new one."""
        timer = Timer()
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            # Explanation generation uses the latest active evidence only. It
            # does not recompute similarity/NLI or rebuild prompts from notes.
            evidence = self.evidence_repository.get_latest_explanation_evidence(
                connection=connection,
                folder_id=folder_id,
                relation_id=relation_id,
            )
            if evidence is None:
                raise ValueError(ERROR_RELATION_EVIDENCE_NOT_FOUND)
            if evidence.explanation:
                # POST behaves as get-or-create: repeat calls return the stored
                # explanation and avoid a second model run.
                logger.info(
                    "explanation existing folder_id=%s relation_id=%s duration_ms=%s",
                    folder_id,
                    relation_id,
                    timer.elapsed_ms,
                )
                return (
                    RelationExplanationRecord(
                        relation_id=evidence.relation_id,
                        explanation=evidence.explanation,
                    ),
                    False,
                )

            generation_timer = Timer()
            explanation = self.explanation_generator.create_explanation(
                evidence.llm_payload,
            )
            generation_ms = generation_timer.elapsed_ms
            self.evidence_repository.update_explanation(
                connection=connection,
                evidence_id=evidence.evidence_id,
                explanation=explanation,
            )
            # process_status records that the relation has moved past confirmed
            # evidence and now also has a generated explanation attached.
            self.relation_repository.update_process_status(
                connection=connection,
                relation_id=evidence.relation_id,
                process_status=PROCESS_STATUS_ADD_EXPLANATION,
            )
            logger.info(
                "explanation generated folder_id=%s relation_id=%s generation_ms=%s duration_ms=%s",
                folder_id,
                evidence.relation_id,
                generation_ms,
                timer.elapsed_ms,
            )
            return (
                RelationExplanationRecord(
                    relation_id=evidence.relation_id,
                    explanation=explanation,
                ),
                True,
            )

    def _ensure_folder_exists(self, connection, folder_id: UUID) -> None:
        folder = self.folder_repository.get_folder(
            connection=connection,
            folder_id=folder_id,
        )
        if folder is None:
            raise ValueError(ERROR_FOLDER_NOT_FOUND)
