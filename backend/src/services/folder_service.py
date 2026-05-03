"""Business operations for folders.

Folder lifecycle logic belongs here; SQL remains in repositories and callers get
simple methods for create, list, open, and soft delete behavior.
"""

from __future__ import annotations

from uuid import UUID

from src.core.config import AppConfig, get_config
from src.core.database import transaction
from src.data.folder_repository import FolderRepository
from src.data.models import FolderRecord
from src.data.note_repository import NoteRepository
from src.data.relation_repository import RelationRepository


class FolderService:
    """Coordinates folder validation and folder-level soft deletes."""

    def __init__(
        self,
        config: AppConfig | None = None,
        folder_repository: FolderRepository | None = None,
        note_repository: NoteRepository | None = None,
        relation_repository: RelationRepository | None = None,
    ) -> None:
        self.config = config or get_config()
        self.folder_repository = folder_repository or FolderRepository()
        self.note_repository = note_repository or NoteRepository()
        self.relation_repository = relation_repository or RelationRepository()

    def create_folder(
        self,
        name: str,
        description: str | None = None,
    ) -> FolderRecord:
        """Create a folder after validating user-facing text."""
        name = self._validate_name(name)
        description = self._normalize_optional_text(description)

        with transaction(self.config) as connection:
            return self.folder_repository.create_folder(
                connection=connection,
                name=name,
                description=description,
            )

    def get_folder(self, folder_id: UUID) -> FolderRecord | None:
        with transaction(self.config) as connection:
            return self.folder_repository.get_folder(
                connection=connection,
                folder_id=folder_id,
            )

    def list_folders(self) -> list[FolderRecord]:
        """Return active folders."""
        with transaction(self.config) as connection:
            return self.folder_repository.list_folders(connection)

    def open_folder(self, folder_id: UUID) -> FolderRecord:
        """Open an active folder and refresh its last_open_at timestamp."""
        with transaction(self.config) as connection:
            folder = self.folder_repository.update_last_open_at(
                connection=connection,
                folder_id=folder_id,
            )
            if folder is None:
                raise ValueError("Folder not found.")
            return folder

    def delete_folder(self, folder_id: UUID) -> None:
        """Soft delete a folder and its child notes, relations, and evidence."""
        with transaction(self.config) as connection:
            folder = self.folder_repository.get_folder(
                connection=connection,
                folder_id=folder_id,
            )
            if folder is None:
                raise ValueError("Folder not found.")

            # Soft deletes do not trigger ON DELETE CASCADE, so child records are
            # marked manually in the same transaction.
            self.relation_repository.soft_delete_relations_by_folder(
                connection=connection,
                folder_id=folder_id,
            )
            self.note_repository.soft_delete_notes_by_folder(
                connection=connection,
                folder_id=folder_id,
            )
            self.folder_repository.soft_delete_folder(
                connection=connection,
                folder_id=folder_id,
            )

    def _validate_name(self, name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValueError("Folder name must not be empty.")
        if len(normalized) > 255:
            raise ValueError("Folder name must be 255 characters or less.")
        return normalized

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None
