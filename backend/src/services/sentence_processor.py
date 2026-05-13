"""AI model wrapper for embeddings, NLI, and overlap evidence.

The service layer uses this class so model loading and inference stay outside
API routes and data repositories.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer

from src.core.model_readiness import resolve_model_reference


NLI_LABEL_MAPPING = ["contradiction", "entailment", "neutral"]


@dataclass(frozen=True)
class NLIResult:
    """NLI output with both raw logits and probabilities."""

    label: str
    raw_scores: list[float]
    probabilities: list[float]

    @property
    def score_by_label(self) -> dict[str, float]:
        return dict(zip(NLI_LABEL_MAPPING, self.probabilities, strict=True))

    @property
    def raw_score_by_label(self) -> dict[str, float]:
        return dict(zip(NLI_LABEL_MAPPING, self.raw_scores, strict=True))


def softmax_np(values: Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    array = array - np.max(array)
    exp_values = np.exp(array)
    return exp_values / exp_values.sum()


class SentenceProcessor:
    """Loads SentenceTransformer and CrossEncoder models for note analysis."""

    def __init__(
        self,
        embedding_model_name: str,
        nli_model_name: str,
        embedding_dimension: int,
    ) -> None:
        self.embedding_dimension = embedding_dimension
        embedding_model_name = resolve_model_reference(embedding_model_name)
        nli_model_name = resolve_model_reference(nli_model_name)
        self.embedding_model = SentenceTransformer(
            embedding_model_name,
            local_files_only=True,
        )
        self.nli_model = CrossEncoder(nli_model_name, local_files_only=True)

    def model_statuses(self) -> dict[str, str]:
        """Return readiness labels for models that are held for note processing."""
        return {
            "embedding": "loaded" if self.embedding_model is not None else "not_loaded",
            "nli": "loaded" if self.nli_model is not None else "not_loaded",
        }

    def embedding(self, sentence: str) -> list[float]:
        """Encode one note and validate that it matches the database vector size."""
        vector = np.asarray(self.embedding_model.encode(sentence), dtype=float).tolist()
        if len(vector) != self.embedding_dimension:
            raise ValueError(
                "Embedding dimension mismatch: "
                f"model returned {len(vector)}, expected {self.embedding_dimension}."
            )
        return vector

    def nli_similarity(self, sentence1: str, sentence2: str) -> NLIResult:
        """Run direction-sensitive NLI for one ordered sentence pair."""
        # cross-encoder/nli-deberta-v3-base returns logits in this fixed order:
        # contradiction, entailment, neutral.
        raw_scores = self.nli_model.predict([(sentence1, sentence2)])[0]
        raw_scores_array = np.asarray(raw_scores, dtype=float)
        probabilities = softmax_np(raw_scores_array).tolist()

        return NLIResult(
            label=NLI_LABEL_MAPPING[int(np.argmax(raw_scores_array))],
            raw_scores=raw_scores_array.tolist(),
            probabilities=probabilities,
        )

    def similarity(self, vector1: Sequence[float], vector2: Sequence[float]) -> float:
        similarity = self.embedding_model.similarity(vector1, vector2)
        return float(np.asarray(similarity).squeeze())

    def word_overlap(self, sentence1: str, sentence2: str) -> list[str]:
        """Return exact normalized word overlap for evidence storage."""
        words1 = set(self._normalize_and_tokenize(sentence1))
        words2 = set(self._normalize_and_tokenize(sentence2))
        return sorted(words1 & words2)

    def similar_words(
        self,
        sentence1: str,
        sentence2: str,
        threshold: float,
    ) -> list[dict[str, float | str]]:
        """Return semantically similar word pairs for relation evidence."""
        words1 = sorted(set(self._normalize_and_tokenize(sentence1)))
        words2 = sorted(set(self._normalize_and_tokenize(sentence2)))

        if not words1 or not words2:
            return []

        embeddings1 = self.embedding_model.encode(words1)
        embeddings2 = self.embedding_model.encode(words2)
        results: list[dict[str, float | str]] = []

        for index1, word1 in enumerate(words1):
            for index2, word2 in enumerate(words2):
                if word1 == word2:
                    continue

                score = self.similarity(embeddings1[index1], embeddings2[index2])
                if score >= threshold:
                    results.append(
                        {
                            "word1": word1,
                            "word2": word2,
                            "score": score,
                        }
                    )

        results.sort(key=lambda item: float(item["score"]), reverse=True)
        return results

    def _normalize_and_tokenize(self, sentence: str) -> list[str]:
        sentence = sentence.lower()
        sentence = re.sub(r"[^\w\s]", "", sentence)
        words = sentence.split()
        stopwords = {
            "i",
            "me",
            "my",
            "you",
            "your",
            "he",
            "she",
            "it",
            "we",
            "they",
            "a",
            "an",
            "the",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "do",
            "does",
            "did",
            "of",
            "to",
            "in",
            "on",
            "at",
            "for",
            "with",
            "from",
            "and",
            "or",
            "but",
            "because",
            "so",
        }
        return [word for word in words if word not in stopwords]
