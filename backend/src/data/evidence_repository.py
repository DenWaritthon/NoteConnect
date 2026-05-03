"""Data access for note_relation_evidence records."""

from __future__ import annotations

import psycopg
from psycopg.types.json import Jsonb

from src.data.models import RelationEvidenceInput


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
