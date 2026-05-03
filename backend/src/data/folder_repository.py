"""Data access for the folder table.

This repository owns folder SQL. Service code should call these methods instead
of querying folder records directly.
"""

from __future__ import annotations

from uuid import UUID

import psycopg

from src.data.models import FolderRecord


class FolderRepository:
    """Maps folder table operations to clean Python records."""

    def create_folder(
        self,
        connection: psycopg.Connection,
        name: str,
        description: str | None,
    ) -> FolderRecord:
        """Insert a new active folder."""
        row = connection.execute(
            """
            INSERT INTO folder (name, description)
            VALUES (%s, %s)
            RETURNING
                folder_id,
                name,
                description,
                created_at,
                updated_at,
                last_open_at
            """,
            (name, description),
        ).fetchone()

        return self._to_folder_record(row)

    def get_folder(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> FolderRecord | None:
        """Return an active folder, or None when it is missing or soft deleted."""
        row = connection.execute(
            """
            SELECT
                folder_id,
                name,
                description,
                created_at,
                updated_at,
                last_open_at
            FROM folder
            WHERE folder_id = %s
              AND deleted_at IS NULL
            """,
            (folder_id,),
        ).fetchone()

        return self._to_folder_record(row) if row else None

    def list_folders(self, connection: psycopg.Connection) -> list[FolderRecord]:
        """List active folders ordered by most recently opened."""
        rows = connection.execute(
            """
            SELECT
                folder_id,
                name,
                description,
                created_at,
                updated_at,
                last_open_at
            FROM folder
            WHERE deleted_at IS NULL
            ORDER BY last_open_at DESC, created_at DESC
            """
        ).fetchall()

        return [self._to_folder_record(row) for row in rows]

    def update_last_open_at(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> FolderRecord | None:
        """Mark a folder as recently opened and return the updated row."""
        row = connection.execute(
            """
            UPDATE folder
            SET last_open_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND deleted_at IS NULL
            RETURNING
                folder_id,
                name,
                description,
                created_at,
                updated_at,
                last_open_at
            """,
            (folder_id,),
        ).fetchone()

        return self._to_folder_record(row) if row else None

    def soft_delete_folder(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> bool:
        """Soft delete a folder by setting deleted_at."""
        row = connection.execute(
            """
            UPDATE folder
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND deleted_at IS NULL
            RETURNING folder_id
            """,
            (folder_id,),
        ).fetchone()

        return row is not None

    def _to_folder_record(self, row: dict) -> FolderRecord:
        return FolderRecord(
            folder_id=row["folder_id"],
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_open_at=row["last_open_at"],
        )
