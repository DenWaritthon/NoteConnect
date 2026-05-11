"""Data access for note_relation_evidence records."""

from __future__ import annotations

from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from src.data.models import (
    RelationEvidenceInput,
    RelationEvidenceRecord,
    RelationExplanationEvidenceRecord,
)


class EvidenceRepository:
    """Persists model evidence for confirmed note relations."""

    def create_evidence(
        self,
        connection: psycopg.Connection,
        evidence: RelationEvidenceInput,
    ) -> None:
        """Insert evidence for a relation using JSONB fields from structured data."""
        # nli_score stores raw model logits by label. PostgreSQL JSONB may display
        # keys in a different order, so readers must use label keys, not position.
        connection.execute(
            """
            INSERT INTO note_relation_evidence (
                relation_id,
                similarity_score,
                nli_score,
                nli_label,
                words_overlap,
                similar_words,
                explanation,
                llm_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                evidence.relation_id,
                evidence.similarity_score,
                Jsonb(evidence.nli_score),
                evidence.nli_label,
                Jsonb(evidence.words_overlap),
                Jsonb(evidence.similar_words),
                evidence.explanation,
                Jsonb(evidence.llm_payload or {}),
            ),
        )

    def get_latest_relation_evidence(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationEvidenceRecord | None:
        """Return the latest active evidence for one active relation in a folder."""
        row = connection.execute(
            """
            SELECT
                relation.relation_id,
                relation.relation_type,
                evidence.similarity_score,
                evidence.nli_label,
                evidence.words_overlap,
                evidence.similar_words
            FROM note_relation AS relation
            JOIN note_relation_evidence AS evidence
              ON evidence.relation_id = relation.relation_id
             AND evidence.deleted_at IS NULL
            WHERE relation.folder_id = %s
              AND relation.relation_id = %s
              AND relation.deleted_at IS NULL
            ORDER BY evidence.created_at DESC
            LIMIT 1
            """,
            (folder_id, relation_id),
        ).fetchone()

        if row is None:
            return None

        return RelationEvidenceRecord(
            relation_id=row["relation_id"],
            relation_type=row["relation_type"],
            similarity_score=(
                float(row["similarity_score"])
                if row["similarity_score"] is not None
                else None
            ),
            nli_label=row["nli_label"],
            words_overlap=row["words_overlap"] or [],
            similar_words=row["similar_words"] or [],
        )

    def get_latest_explanation_evidence(
        self,
        connection: psycopg.Connection,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationExplanationEvidenceRecord | None:
        """Return latest active evidence with explanation payload for one relation."""
        row = connection.execute(
            """
            SELECT
                evidence.evidence_id,
                relation.relation_id,
                evidence.explanation,
                evidence.llm_payload
            FROM note_relation AS relation
            JOIN note_relation_evidence AS evidence
              ON evidence.relation_id = relation.relation_id
             AND evidence.deleted_at IS NULL
            WHERE relation.folder_id = %s
              AND relation.relation_id = %s
              AND relation.deleted_at IS NULL
            ORDER BY evidence.created_at DESC
            LIMIT 1
            """,
            (folder_id, relation_id),
        ).fetchone()

        if row is None:
            return None

        return RelationExplanationEvidenceRecord(
            evidence_id=row["evidence_id"],
            relation_id=row["relation_id"],
            explanation=row["explanation"],
            llm_payload=row["llm_payload"] or {},
        )

    def update_explanation(
        self,
        connection: psycopg.Connection,
        evidence_id: UUID,
        explanation: str,
    ) -> None:
        """Store explanation on an existing evidence row."""
        connection.execute(
            """
            UPDATE note_relation_evidence
            SET explanation = %s,
                updated_at = NOW()
            WHERE evidence_id = %s
              AND deleted_at IS NULL
            """,
            (explanation, evidence_id),
        )
