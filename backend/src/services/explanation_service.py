"""Business workflow for relation explanations."""

from __future__ import annotations

from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.database import transaction
from src.data.evidence_repository import EvidenceRepository
from src.data.folder_repository import FolderRepository
from src.data.models import RelationExplanationRecord
from src.data.relation_repository import RelationRepository
from src.services.explanation_generator import ExplanationGenerator


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
            evidence = self.evidence_repository.get_latest_explanation_evidence(
                connection=connection,
                folder_id=folder_id,
                relation_id=relation_id,
            )
            if evidence is None:
                raise ValueError("Relation evidence not found.")
            if not evidence.explanation:
                raise ValueError("Explanation not found.")
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
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            evidence = self.evidence_repository.get_latest_explanation_evidence(
                connection=connection,
                folder_id=folder_id,
                relation_id=relation_id,
            )
            if evidence is None:
                raise ValueError("Relation evidence not found.")
            if evidence.explanation:
                return (
                    RelationExplanationRecord(
                        relation_id=evidence.relation_id,
                        explanation=evidence.explanation,
                    ),
                    False,
                )

            explanation = self.explanation_generator.create_explanation(
                evidence.llm_payload,
            )
            self.evidence_repository.update_explanation(
                connection=connection,
                evidence_id=evidence.evidence_id,
                explanation=explanation,
            )
            self.relation_repository.update_process_status(
                connection=connection,
                relation_id=evidence.relation_id,
                process_status="add_explanation",
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
            raise ValueError("Folder not found.")
