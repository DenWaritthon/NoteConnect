from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import re
import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer


NLI_LABEL_MAPPING = ["contradiction", "entailment", "neutral"]


@dataclass(frozen=True)
class NLIResult:
    label: str
    raw_scores: list[float]
    probabilities: list[float]

    @property
    def neutral_margin(self) -> float:
        """Margin from raw logits: neutral - max(contradiction, entailment)."""
        return self.raw_scores[2] - max(self.raw_scores[0], self.raw_scores[1])


def softmax_np(values: Sequence[float]) -> np.ndarray:
    """Numerically stable softmax for numpy/list logits."""
    array = np.asarray(values, dtype=float)
    array = array - np.max(array)
    exp_values = np.exp(array)
    return exp_values / exp_values.sum()

class SentenceProcessor:
    def __init__(
        self,
        embedding_model_name: str = "sentence-transformers/all-mpnet-base-v2",
        nli_model_name: str = "cross-encoder/nli-deberta-v3-base",
    ) -> None:
        self.model = SentenceTransformer(embedding_model_name)
        self.model_nli = CrossEncoder(nli_model_name)

    def embedding(self, sentence: str) -> np.ndarray:
        """Create an embedding vector for one sentence/note."""
        return self.model.encode(sentence)

    def similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Return cosine similarity as a plain float."""
        similarity = self.model.similarity(vector1, vector2)
        return float(np.asarray(similarity).squeeze())

    def nli_similarity(self, sentence1: str, sentence2: str) -> NLIResult:
        """
        Run NLI cross-encoder.

        Output order from cross-encoder/nli-deberta-v3-base:
        [contradiction, entailment, neutral]
        """
        raw_scores = self.model_nli.predict([(sentence1, sentence2)])[0]
        raw_scores_array = np.asarray(raw_scores, dtype=float)

        label = NLI_LABEL_MAPPING[int(np.argmax(raw_scores_array))]
        probabilities = softmax_np(raw_scores_array).tolist()

        return NLIResult(
            label=label,
            raw_scores=raw_scores_array.tolist(),
            probabilities=probabilities,
        )
    
    def _normalize_and_tokenize(self, sentence):
        """
        Normalize and tokenize sentence into words.
        """
        sentence = sentence.lower()
        sentence = re.sub(r"[^\w\s]", "", sentence)
        words = sentence.split()
        stopwords = {
            "i", "me", "my", "you", "your", "he", "she", "it", "we", "they",
            "a", "an", "the",
            "is", "am", "are", "was", "were", "be", "been", "being",
            "do", "does", "did",
            "of", "to", "in", "on", "at", "for", "with", "from",
            "and", "or", "but", "because", "so"
        }

        return [word for word in words if word not in stopwords]
    
    def word_overlap(self, sentence1: str, sentence2: str) -> list[str]:
        """
        Find exact word overlap between two sentences after normalization.
        """

        words1 = set(self._normalize_and_tokenize(sentence1))
        words2 = set(self._normalize_and_tokenize(sentence2))

        return sorted(words1 & words2)

    def similar_words(self, sentence1: str, sentence2: str, threshold: float = 0.55) -> list[dict]:
        """
        Find semantically similar words between two sentences.
        Uses embedding similarity (cosine) via self.similarity().
        """

        words1 = self._normalize_and_tokenize(sentence1)
        words2 = self._normalize_and_tokenize(sentence2)

        words1 = sorted(set(words1))
        words2 = sorted(set(words2))

        if not words1 or not words2:
            return []

        # encode เป็น batch (สำคัญ: เร็วกว่า encode ทีละคำ)
        embeddings1 = self.model.encode(words1)
        embeddings2 = self.model.encode(words2)

        results = []

        for i, w1 in enumerate(words1):
            for j, w2 in enumerate(words2):
                if w1 == w2:
                    continue  # ข้าม exact match (ไปอยู่ word_overlap แทน)

                score = self.similarity(embeddings1[i], embeddings2[j])

                if score >= threshold:
                    results.append({
                        "word1": w1,
                        "word2": w2,
                        "score": float(score)
                    })

        # sort จาก similarity สูง → ต่ำ
        results.sort(key=lambda x: x["score"], reverse=True)

        return results