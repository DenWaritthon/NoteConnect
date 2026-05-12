"""Read operations for relation API endpoints.

The relation decision logic stays in relation_service.py. This service exists
for API read workflows that need relation summaries or stored evidence.
"""

from __future__ import annotations

from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.constants import ERROR_FOLDER_NOT_FOUND, ERROR_RELATION_EVIDENCE_NOT_FOUND
from src.core.database import transaction
from src.data.evidence_repository import EvidenceRepository
from src.data.folder_repository import FolderRepository
from src.data.models import RelationEvidenceRecord, RelationSummary
from src.data.relation_repository import RelationRepository


class RelationQueryService:
    """Coordinates relation reads without recomputing AI results."""

    def __init__(
        self,
        config: AppConfig | None = None,
        folder_repository: FolderRepository | None = None,
        relation_repository: RelationRepository | None = None,
        evidence_repository: EvidenceRepository | None = None,
    ) -> None:
        self.config = config or get_config()
        self.folder_repository = folder_repository or FolderRepository()
        self.relation_repository = relation_repository or RelationRepository()
        self.evidence_repository = evidence_repository or EvidenceRepository()

    def list_relations(self, folder_id: UUID) -> list[RelationSummary]:
        """List active relation summaries for an active folder."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            return self.relation_repository.list_relations(
                connection=connection,
                folder_id=folder_id,
            )

    def get_relation_evidence(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationEvidenceRecord:
        """Return stored evidence for one relation without model inference."""
        with transaction(self.config) as connection:
            self._ensure_folder_exists(connection, folder_id)
            evidence = self.evidence_repository.get_latest_relation_evidence(
                connection=connection,
                folder_id=folder_id,
                relation_id=relation_id,
            )
            if evidence is None:
                raise ValueError(ERROR_RELATION_EVIDENCE_NOT_FOUND)
            return evidence

    def _ensure_folder_exists(self, connection, folder_id: UUID) -> None:
        folder = self.folder_repository.get_folder(
            connection=connection,
            folder_id=folder_id,
        )
        if folder is None:
            raise ValueError(ERROR_FOLDER_NOT_FOUND)
