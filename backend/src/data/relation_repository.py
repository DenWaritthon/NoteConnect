"""Data access for noteconnect_note_relation records.

Relation writes, duplicate prevention, listing, and soft delete behavior live
here so services can coordinate the pipeline without owning SQL.
"""

from __future__ import annotations

from uuid import UUID

import psycopg

from src.core.constants import PROCESS_STATUS_RELATION_CONFIRMED
from src.data.models import RelationRecord, RelationSummary


class RelationRepository:
    """Owns noteconnect_note_relation queries and relation soft-delete behavior."""

    def create_relation(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        note_id_1: UUID,
        note_id_2: UUID,
        relation_type: str,
        process_status: str = PROCESS_STATUS_RELATION_CONFIRMED,
    ) -> RelationRecord:
        """Create or revive a relation for a normalized noteconnect_note pair."""
        left_id, right_id = self.normalize_pair(note_id_1, note_id_2)
        # ON CONFLICT revives a previously soft-deleted pair and refreshes its
        # current classification instead of creating duplicate active relations.
        row = connection.execute(
            """
            INSERT INTO noteconnect_note_relation (
                folder_id,
                note_1_id,
                note_2_id,
                relation_type,
                process_status
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (folder_id, note_1_id, note_2_id)
            DO UPDATE SET
                relation_type = EXCLUDED.relation_type,
                process_status = EXCLUDED.process_status,
                deleted_at = NULL,
                updated_at = NOW()
            RETURNING
                relation_id,
                folder_id,
                note_1_id,
                note_2_id,
                relation_type,
                process_status
            """,
            (folder_id, left_id, right_id, relation_type, process_status),
        ).fetchone()

        return RelationRecord(
            relation_id=row["relation_id"],
            folder_id=row["folder_id"],
            note_1_id=row["note_1_id"],
            note_2_id=row["note_2_id"],
            relation_type=row["relation_type"],
            process_status=row["process_status"],
        )

    def soft_delete_relations_for_note(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        note_id: UUID,
    ) -> int:
        """Soft delete active relations and evidence connected to one noteconnect_note."""
        connection.execute(
            """
            UPDATE noteconnect_note_relation_evidence
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE relation_id IN (
                SELECT relation_id
                FROM noteconnect_note_relation
                WHERE folder_id = %s
                  AND (note_1_id = %s OR note_2_id = %s)
                  AND deleted_at IS NULL
            )
              AND deleted_at IS NULL
            """,
            (folder_id, note_id, note_id),
        )
        relation_result = connection.execute(
            """
            UPDATE noteconnect_note_relation
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND (note_1_id = %s OR note_2_id = %s)
              AND deleted_at IS NULL
            """,
            (folder_id, note_id, note_id),
        )

        return relation_result.rowcount if relation_result.rowcount is not None else 0

    def soft_delete_relations_by_folder(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> int:
        """Soft delete all active relations and evidence in a noteconnect_folder."""
        connection.execute(
            """
            UPDATE noteconnect_note_relation_evidence
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE relation_id IN (
                SELECT relation_id
                FROM noteconnect_note_relation
                WHERE folder_id = %s
                  AND deleted_at IS NULL
            )
              AND deleted_at IS NULL
            """,
            (folder_id,),
        )
        relation_result = connection.execute(
            """
            UPDATE noteconnect_note_relation
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND deleted_at IS NULL
            """,
            (folder_id,),
        )

        return relation_result.rowcount if relation_result.rowcount is not None else 0

    def list_relations(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> list[RelationSummary]:
        """List active relations with their latest active evidence summary."""
        # LATERAL keeps the relation list lightweight while still exposing the
        # newest evidence snapshot needed by clients.
        rows = connection.execute(
            """
            SELECT
                relation.relation_id,
                relation.folder_id,
                relation.note_1_id,
                note_1.sentence AS note_1_sentence,
                relation.note_2_id,
                note_2.sentence AS note_2_sentence,
                relation.relation_type,
                relation.process_status,
                evidence.similarity_score,
                evidence.nli_label
            FROM noteconnect_note_relation AS relation
            JOIN noteconnect_note AS note_1
              ON note_1.note_id = relation.note_1_id
             AND note_1.deleted_at IS NULL
            JOIN noteconnect_note AS note_2
              ON note_2.note_id = relation.note_2_id
             AND note_2.deleted_at IS NULL
            LEFT JOIN LATERAL (
                SELECT similarity_score, nli_label
                FROM noteconnect_note_relation_evidence
                WHERE relation_id = relation.relation_id
                  AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
            ) AS evidence ON TRUE
            WHERE relation.folder_id = %s
              AND relation.deleted_at IS NULL
            ORDER BY relation.created_at ASC
            """,
            (folder_id,),
        ).fetchall()

        return [
            RelationSummary(
                relation_id=row["relation_id"],
                folder_id=row["folder_id"],
                note_1_id=row["note_1_id"],
                note_1_sentence=row["note_1_sentence"],
                note_2_id=row["note_2_id"],
                note_2_sentence=row["note_2_sentence"],
                relation_type=row["relation_type"],
                process_status=row["process_status"],
                similarity_score=(
                    float(row["similarity_score"])
                    if row["similarity_score"] is not None
                    else None
                ),
                nli_label=row["nli_label"],
            )
            for row in rows
        ]

    def update_process_status(
        self,
        connection: psycopg.Connection,
        relation_id: UUID,
        process_status: str,
    ) -> None:
        """Update process status for one active relation."""
        connection.execute(
            """
            UPDATE noteconnect_note_relation
            SET process_status = %s,
                updated_at = NOW()
            WHERE relation_id = %s
              AND deleted_at IS NULL
            """,
            (process_status, relation_id),
        )

    def normalize_pair(self, note_id_1: UUID, note_id_2: UUID) -> tuple[UUID, UUID]:
        """Return a stable pair direction for the database uniqueness rule."""
        if note_id_1 == note_id_2:
            raise ValueError("A noteconnect_note cannot be related to itself.")

        # Keep pair direction stable so the unique constraint prevents duplicates
        # even when the same logical relation is discovered from either noteconnect_note.
        return tuple(sorted((note_id_1, note_id_2), key=str))
