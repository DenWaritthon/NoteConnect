"""Relation decision logic for similarity and NLI results.

This module translates model outputs into database relation types without doing
database work itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.services.sentence_processor import NLIResult


@dataclass(frozen=True)
class RelationDecision:
    """A relation accepted by the AI pipeline and ready to persist."""

    relation_type: str
    nli_label: str
    nli_score: dict[str, float]
    decision_stage: str


class RelationService:
    """Classifies candidate note pairs into allowed relation types."""

    def __init__(self, similarity_threshold: float, threshold_scale: float) -> None:
        self.similarity_threshold = similarity_threshold
        self.threshold_scale = threshold_scale

    @property
    def neutral_threshold(self) -> float:
        return self.similarity_threshold + (
            1.0 - self.similarity_threshold
        ) * self.threshold_scale

    def classify(
        self,
        similarity_score: float,
        nli_result: NLIResult,
    ) -> RelationDecision | None:
        """Return a relation decision when similarity and NLI pass thresholds."""
        # Base similarity is the first gate for every candidate returned from
        # pgvector; NLI can only confirm or reject candidates that pass it.
        if similarity_score < self.similarity_threshold:
            return None

        if nli_result.label == "entailment":
            return RelationDecision(
                relation_type="related_entailment",
                nli_label=nli_result.label,
                nli_score=nli_result.raw_score_by_label,
                decision_stage="nli_entailment",
            )

        if nli_result.label == "contradiction":
            return RelationDecision(
                relation_type="related_conflict",
                nli_label=nli_result.label,
                nli_score=nli_result.raw_score_by_label,
                decision_stage="nli_contradiction",
            )

        if nli_result.label == "neutral" and similarity_score >= self.neutral_threshold:
            # Neutral pairs need a stricter similarity check because NLI did not
            # directly confirm entailment or contradiction.
            return RelationDecision(
                relation_type="related_semantic",
                nli_label=nli_result.label,
                nli_score=nli_result.raw_score_by_label,
                decision_stage="strict_similarity_check",
            )

        return None
