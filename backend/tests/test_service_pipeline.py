"""Service-level tests for relation payload and explanation workflow behavior."""

from __future__ import annotations

import sys
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.core.config import AppConfig, DatabaseConfig
from src.data.models import (
    FolderRecord,
    NoteRecord,
    RelationExplanationEvidenceRecord,
    SimilarNote,
)
from src.services.explanation_generator import ExplanationGenerator
from src.services.explanation_service import ExplanationService
from src.services.note_service import NoteService
from src.services.sentence_processor import NLIResult


FOLDER_ID = UUID("11111111-1111-1111-1111-111111111111")
NOTE_1_ID = UUID("22222222-2222-2222-2222-222222222222")
NOTE_2_ID = UUID("22222222-2222-2222-2222-222222222223")
RELATION_ID = UUID("33333333-3333-3333-3333-333333333333")
EVIDENCE_ID = UUID("44444444-4444-4444-4444-444444444444")
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def test_config() -> AppConfig:
    return AppConfig(
        app_env="test",
        app_host="127.0.0.1",
        app_port=8000,
        enable_docs=True,
        ready_check_database=False,
        log_level="INFO",
        database=DatabaseConfig(
            host="localhost",
            port=5432,
            name="noteconnect_test",
            user="postgres",
            password="",
            connect_timeout=10,
        ),
        api_secret_key="test-secret",
        api_key_header_name="X-API-Key",
        embedding_model="stub",
        nli_model="stub",
        explanation_model="stub",
        explanation_max_new_tokens=32,
        explanation_load_mode="startup",
        embedding_dimension=3,
        similarity_threshold=0.4,
        threshold_scale=0.2,
        similarity_top_k=10,
        similar_word_threshold=0.55,
    )


@contextmanager
def fake_transaction(_config):
    yield object()


class FakeFolderRepository:
    def get_folder(self, connection, folder_id: UUID):
        return SimpleNamespace(folder_id=folder_id)

    def touch_updated_at(self, connection, folder_id: UUID) -> None:
        return None


class FakeNoteRepository:
    def find_similar_notes(
        self,
        connection,
        folder_id: UUID,
        source_note_id: UUID,
        query_embedding: list[float],
        top_k: int,
        threshold: float,
    ) -> list[SimilarNote]:
        return [
            SimilarNote(
                note_id=NOTE_2_ID,
                folder_id=folder_id,
                sentence="The animal is on the table.",
                similarity_score=0.91,
            )
        ]


class FakeRelationRepository:
    def __init__(self) -> None:
        self.created_process_status: str | None = None
        self.updated_process_status: str | None = None

    def create_relation(
        self,
        connection,
        folder_id: UUID,
        note_id_1: UUID,
        note_id_2: UUID,
        relation_type: str,
        process_status: str,
    ):
        self.created_process_status = process_status
        return SimpleNamespace(relation_id=RELATION_ID)

    def update_process_status(
        self,
        connection,
        relation_id: UUID,
        process_status: str,
    ) -> None:
        self.updated_process_status = process_status


class CapturingEvidenceRepository:
    def __init__(
        self,
        evidence: RelationExplanationEvidenceRecord | None = None,
    ) -> None:
        self.evidence = evidence
        self.created_evidence = None
        self.updated_explanation: tuple[UUID, str] | None = None

    def create_evidence(self, connection, evidence) -> None:
        self.created_evidence = evidence

    def get_latest_explanation_evidence(
        self,
        connection,
        folder_id: UUID,
        relation_id: UUID,
    ):
        return self.evidence

    def update_explanation(
        self,
        connection,
        evidence_id: UUID,
        explanation: str,
    ) -> None:
        self.updated_explanation = (evidence_id, explanation)


class FakeSentenceProcessor:
    def nli_similarity(self, sentence1: str, sentence2: str) -> NLIResult:
        return NLIResult(
            label="entailment",
            raw_scores=[-1.0, 4.0, -2.0],
            probabilities=[0.01, 0.98, 0.01],
        )

    def word_overlap(self, sentence1: str, sentence2: str) -> list[str]:
        return ["table"]

    def similar_words(
        self,
        sentence1: str,
        sentence2: str,
        threshold: float,
    ) -> list[dict[str, float | str]]:
        return [{"word1": "pig", "word2": "animal", "score": 0.82}]


class FakeExplanationGenerator:
    def __init__(self) -> None:
        self.payload = None

    def create_explanation(self, llm_payload: dict[str, object]) -> str:
        self.payload = llm_payload
        return "Both notes describe an animal being on a table."


class CountingLazyExplanationGenerator(ExplanationGenerator):
    def __init__(self) -> None:
        super().__init__(
            model_name="stub",
            max_new_tokens=32,
            load_mode="lazy",
        )
        self.load_count = 0
        self.unload_count = 0

    def load(self) -> None:
        self.load_count += 1
        self._model = object()
        self._tokenizer = object()

    def unload(self) -> None:
        self.unload_count += 1
        self._model = None
        self._tokenizer = None

    def _generate(self, llm_payload: dict[str, object]) -> str:
        self.assert_model_is_loaded()
        return f"Generated from {llm_payload['note_1']}"

    def assert_model_is_loaded(self) -> None:
        if self._model is None or self._tokenizer is None:
            raise AssertionError("Model should be loaded during generation.")


class ServicePipelineTests(unittest.TestCase):
    def test_new_relation_evidence_uses_agents_llm_payload_shape(self) -> None:
        relation_repository = FakeRelationRepository()
        evidence_repository = CapturingEvidenceRepository()
        service = NoteService(
            config=test_config(),
            sentence_processor=FakeSentenceProcessor(),
            folder_repository=FakeFolderRepository(),
            note_repository=FakeNoteRepository(),
            relation_repository=relation_repository,
            evidence_repository=evidence_repository,
        )
        source_note = NoteRecord(
            note_id=NOTE_1_ID,
            folder_id=FOLDER_ID,
            sentence="The pig is on the table.",
            created_at=NOW,
            updated_at=NOW,
        )

        service._rebuild_relations_for_note(
            connection=object(),
            folder_id=FOLDER_ID,
            source_note=source_note,
            source_embedding=[0.1, 0.2, 0.3],
        )

        evidence = evidence_repository.created_evidence
        self.assertIsNotNone(evidence)
        self.assertEqual(relation_repository.created_process_status, "relation_confirmed")
        self.assertEqual(
            set(evidence.llm_payload),
            {"note_1", "note_2", "system_prompt", "question_prompt"},
        )
        self.assertEqual(evidence.llm_payload["note_1"], "The pig is on the table.")
        self.assertEqual(evidence.llm_payload["note_2"], "The animal is on the table.")

    def test_create_explanation_generates_once_and_updates_status(self) -> None:
        payload = {
            "note_1": "The pig is on the table.",
            "note_2": "The animal is on the table.",
            "system_prompt": ["Explain the relation."],
            "question_prompt": ["How are they related?"],
        }
        evidence_repository = CapturingEvidenceRepository(
            RelationExplanationEvidenceRecord(
                evidence_id=EVIDENCE_ID,
                relation_id=RELATION_ID,
                explanation=None,
                llm_payload=payload,
            )
        )
        relation_repository = FakeRelationRepository()
        generator = FakeExplanationGenerator()
        service = ExplanationService(
            config=test_config(),
            explanation_generator=generator,
            folder_repository=FakeFolderRepository(),
            relation_repository=relation_repository,
            evidence_repository=evidence_repository,
        )

        with patch("src.services.explanation_service.transaction", fake_transaction):
            explanation, generated = service.create_explanation(
                folder_id=FOLDER_ID,
                relation_id=RELATION_ID,
            )

        self.assertTrue(generated)
        self.assertEqual(explanation.relation_id, RELATION_ID)
        self.assertEqual(
            explanation.explanation,
            "Both notes describe an animal being on a table.",
        )
        self.assertEqual(generator.payload, payload)
        self.assertEqual(
            evidence_repository.updated_explanation,
            (EVIDENCE_ID, "Both notes describe an animal being on a table."),
        )
        self.assertEqual(relation_repository.updated_process_status, "add_explanation")

    def test_get_explanation_does_not_generate_when_missing(self) -> None:
        evidence_repository = CapturingEvidenceRepository(
            RelationExplanationEvidenceRecord(
                evidence_id=EVIDENCE_ID,
                relation_id=RELATION_ID,
                explanation=None,
                llm_payload={},
            )
        )
        generator = FakeExplanationGenerator()
        service = ExplanationService(
            config=test_config(),
            explanation_generator=generator,
            folder_repository=FakeFolderRepository(),
            relation_repository=FakeRelationRepository(),
            evidence_repository=evidence_repository,
        )

        with patch("src.services.explanation_service.transaction", fake_transaction):
            with self.assertRaisesRegex(ValueError, "Explanation not found."):
                service.get_explanation(
                    folder_id=FOLDER_ID,
                    relation_id=RELATION_ID,
                )

        self.assertIsNone(generator.payload)
        self.assertIsNone(evidence_repository.updated_explanation)

    def test_lazy_explanation_generator_loads_and_unloads_per_call(self) -> None:
        payload = {
            "note_1": "The pig is on the table.",
            "note_2": "The animal is on the table.",
            "system_prompt": ["Explain the relation."],
            "question_prompt": ["How are they related?"],
        }
        generator = CountingLazyExplanationGenerator()

        first = generator.create_explanation(payload)
        second = generator.create_explanation(payload)

        self.assertEqual(first, "Generated from The pig is on the table.")
        self.assertEqual(second, "Generated from The pig is on the table.")
        self.assertEqual(generator.load_count, 2)
        self.assertEqual(generator.unload_count, 2)
        self.assertIsNone(generator._model)
        self.assertIsNone(generator._tokenizer)


if __name__ == "__main__":
    unittest.main()
