"""Data access for notes and pgvector similarity search.

This module owns all SQL for the noteconnect_note table. Similarity search is intentionally
performed in PostgreSQL so pgvector indexes can be used in production.
"""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

import psycopg
from pgvector import Vector

from src.data.models import NoteRecord, SimilarNote


class NoteRepository:
    """Maps noteconnect_note table operations to records used by the service layer."""

    def create_note(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        sentence: str,
        embedding: Sequence[float],
    ) -> NoteRecord:
        """Insert a noteconnect_note with its already generated embedding."""
        row = connection.execute(
            """
            INSERT INTO noteconnect_note (folder_id, sentence, sentence_embedding)
            VALUES (%s, %s, %s)
            RETURNING note_id, folder_id, sentence, created_at, updated_at
            """,
            (folder_id, sentence, Vector(embedding)),
        ).fetchone()

        return self._to_note_record(row)

    def update_note(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        note_id: UUID,
        sentence: str,
        embedding: Sequence[float],
    ) -> NoteRecord | None:
        """Update a noteconnect_note sentence and replace its embedding."""
        row = connection.execute(
            """
            UPDATE noteconnect_note
            SET sentence = %s,
                sentence_embedding = %s,
                updated_at = NOW()
            WHERE folder_id = %s
              AND note_id = %s
              AND deleted_at IS NULL
            RETURNING note_id, folder_id, sentence, created_at, updated_at
            """,
            (sentence, Vector(embedding), folder_id, note_id),
        ).fetchone()

        return self._to_note_record(row) if row else None

    def soft_delete_note(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        note_id: UUID,
    ) -> bool:
        """Soft delete one active noteconnect_note in a noteconnect_folder."""
        row = connection.execute(
            """
            UPDATE noteconnect_note
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND note_id = %s
              AND deleted_at IS NULL
            RETURNING note_id
            """,
            (folder_id, note_id),
        ).fetchone()

        return row is not None

    def get_note(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        note_id: UUID,
    ) -> NoteRecord | None:
        """Return one active noteconnect_note from a noteconnect_folder."""
        row = connection.execute(
            """
            SELECT note_id, folder_id, sentence, created_at, updated_at
            FROM noteconnect_note
            WHERE folder_id = %s
              AND note_id = %s
              AND deleted_at IS NULL
            """,
            (folder_id, note_id),
        ).fetchone()

        return self._to_note_record(row) if row else None

    def list_notes(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> list[NoteRecord]:
        """List active notes for a noteconnect_folder."""
        rows = connection.execute(
            """
            SELECT note_id, folder_id, sentence, created_at, updated_at
            FROM noteconnect_note
            WHERE folder_id = %s
              AND deleted_at IS NULL
            ORDER BY created_at ASC
            """,
            (folder_id,),
        ).fetchall()

        return [self._to_note_record(row) for row in rows]

    def soft_delete_notes_by_folder(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
    ) -> int:
        """Soft delete all active notes in a noteconnect_folder."""
        result = connection.execute(
            """
            UPDATE noteconnect_note
            SET deleted_at = NOW(),
                updated_at = NOW()
            WHERE folder_id = %s
              AND deleted_at IS NULL
            """,
            (folder_id,),
        )

        return result.rowcount if result.rowcount is not None else 0

    def find_similar_notes(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        source_note_id: UUID,
        query_embedding: Sequence[float],
        top_k: int,
        threshold: float,
    ) -> list[SimilarNote]:
        """Find active notes nearest to an embedding using pgvector cosine distance."""
        # Similarity must stay in PostgreSQL; Python-side pairwise comparison
        # would bypass pgvector indexes and break the production search path.
        rows = connection.execute(
            """
            SELECT *
            FROM (
                SELECT
                    note_id,
                    folder_id,
                    sentence,
                    1 - (sentence_embedding <=> %s) AS similarity_score
                FROM noteconnect_note
                WHERE folder_id = %s
                  AND note_id != %s
                  AND sentence_embedding IS NOT NULL
                  AND deleted_at IS NULL
                ORDER BY sentence_embedding <=> %s
                LIMIT %s
            ) AS candidates
            WHERE similarity_score >= %s
            ORDER BY similarity_score DESC
            """,
            (
                Vector(query_embedding),
                folder_id,
                source_note_id,
                Vector(query_embedding),
                top_k,
                threshold,
            ),
        ).fetchall()

        return [
            SimilarNote(
                note_id=row["note_id"],
                folder_id=row["folder_id"],
                sentence=row["sentence"],
                similarity_score=float(row["similarity_score"]),
            )
            for row in rows
        ]

    def _to_note_record(self, row: dict) -> NoteRecord:
        return NoteRecord(
            note_id=row["note_id"],
            folder_id=row["folder_id"],
            sentence=row["sentence"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
