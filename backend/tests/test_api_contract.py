"""Fast API contract tests using in-memory service doubles."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("API_SECRET_KEY", "test-secret")
os.environ.setdefault("API_KEY_HEADER_NAME", "X-API-Key")

from src.api.routers import folder_router, health_router, note_router, relation_router
from src.data.models import (
    FolderRecord,
    NoteRecord,
    RelationEvidenceRecord,
    RelationExplanationRecord,
    RelationSummary,
)


FOLDER_ID = UUID("11111111-1111-1111-1111-111111111111")
NOTE_1_ID = UUID("22222222-2222-2222-2222-222222222222")
NOTE_2_ID = UUID("22222222-2222-2222-2222-222222222223")
RELATION_ID = UUID("33333333-3333-3333-3333-333333333333")
NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


class FakeFolderService:
    def __init__(self) -> None:
        self.folder = FolderRecord(
            folder_id=FOLDER_ID,
            name="Work",
            description="Notes",
            created_at=NOW,
            updated_at=NOW,
            last_open_at=NOW,
        )
        self.update_calls: list[dict[str, object]] = []

    def create_folder(self, name: str, description: str | None = None) -> FolderRecord:
        return FolderRecord(
            folder_id=FOLDER_ID,
            name=name,
            description=description,
            created_at=NOW,
            updated_at=NOW,
            last_open_at=NOW,
        )

    def list_folders(self) -> list[FolderRecord]:
        return [self.folder]

    def get_folder(self, folder_id: UUID) -> FolderRecord | None:
        return self.folder if folder_id == FOLDER_ID else None

    def open_folder(self, folder_id: UUID) -> FolderRecord:
        if folder_id != FOLDER_ID:
            raise ValueError("Folder not found.")
        return self.folder

    def update_folder(
        self,
        folder_id: UUID,
        name: str | None = None,
        description: str | None = None,
        update_description: bool = False,
    ) -> FolderRecord:
        if folder_id != FOLDER_ID:
            raise ValueError("Folder not found.")
        self.update_calls.append(
            {
                "name": name,
                "description": description,
                "update_description": update_description,
            }
        )
        return FolderRecord(
            folder_id=FOLDER_ID,
            name=name or self.folder.name,
            description=description if update_description else self.folder.description,
            created_at=NOW,
            updated_at=NOW,
            last_open_at=NOW,
        )

    def delete_folder(self, folder_id: UUID) -> None:
        if folder_id != FOLDER_ID:
            raise ValueError("Folder not found.")


class FakeNoteService:
    def create_note(self, folder_id: UUID, sentence: str) -> NoteRecord:
        return NoteRecord(
            note_id=NOTE_1_ID,
            folder_id=folder_id,
            sentence=sentence,
            created_at=NOW,
            updated_at=NOW,
        )

    def list_notes(self, folder_id: UUID) -> list[NoteRecord]:
        return [
            NoteRecord(
                note_id=NOTE_1_ID,
                folder_id=folder_id,
                sentence="The pig is on the table.",
                created_at=NOW,
                updated_at=NOW,
            )
        ]

    def get_note(self, folder_id: UUID, note_id: UUID) -> NoteRecord:
        if note_id != NOTE_1_ID:
            raise ValueError("Note not found.")
        return NoteRecord(
            note_id=note_id,
            folder_id=folder_id,
            sentence="The pig is on the table.",
            created_at=NOW,
            updated_at=NOW,
        )

    def update_note(self, folder_id: UUID, note_id: UUID, sentence: str) -> NoteRecord:
        if note_id != NOTE_1_ID:
            raise ValueError("Note not found.")
        return NoteRecord(
            note_id=note_id,
            folder_id=folder_id,
            sentence=sentence,
            created_at=NOW,
            updated_at=NOW,
        )

    def delete_note(self, folder_id: UUID, note_id: UUID) -> None:
        if note_id != NOTE_1_ID:
            raise ValueError("Note not found.")


class FakeRelationQueryService:
    def list_relations(self, folder_id: UUID) -> list[RelationSummary]:
        return [
            RelationSummary(
                relation_id=RELATION_ID,
                folder_id=folder_id,
                note_1_id=NOTE_1_ID,
                note_1_sentence="The pig is on the table.",
                note_2_id=NOTE_2_ID,
                note_2_sentence="The animal is on the table.",
                relation_type="related_entailment",
                process_status="relation_confirmed",
                similarity_score=0.91,
                nli_label="entailment",
            )
        ]

    def get_relation_evidence(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationEvidenceRecord:
        if relation_id != RELATION_ID:
            raise ValueError("Relation evidence not found.")
        return RelationEvidenceRecord(
            relation_id=relation_id,
            relation_type="related_entailment",
            similarity_score=0.91,
            nli_label="entailment",
            words_overlap=["table"],
            similar_words=[{"word1": "pig", "word2": "animal", "score": 0.82}],
        )


class FakeExplanationService:
    def __init__(self) -> None:
        self.generated = False

    def get_explanation(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> RelationExplanationRecord:
        if not self.generated:
            raise ValueError("Explanation not found.")
        return RelationExplanationRecord(
            relation_id=relation_id,
            explanation="Both notes describe an animal being on a table.",
        )

    def create_explanation(
        self,
        folder_id: UUID,
        relation_id: UUID,
    ) -> tuple[RelationExplanationRecord, bool]:
        was_generated = not self.generated
        self.generated = True
        return (
            RelationExplanationRecord(
                relation_id=relation_id,
                explanation="Both notes describe an animal being on a table.",
            ),
            was_generated,
        )


def build_test_app() -> FastAPI:
    app = FastAPI(title="NoteConnect API Test")
    app.include_router(health_router.router)
    app.include_router(folder_router.router)
    app.include_router(note_router.router)
    app.include_router(relation_router.router)
    app.state.config = SimpleNamespace(
        ready_check_database=False,
        explanation_load_mode="lazy",
    )
    app.state.folder_service = FakeFolderService()
    app.state.note_service = FakeNoteService()
    app.state.relation_query_service = FakeRelationQueryService()
    app.state.explanation_service = FakeExplanationService()
    return app


class ApiContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = build_test_app()
        self.client = TestClient(self.app)
        self.headers = {"X-API-Key": "test-secret"}

    def test_health_is_public(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ready_is_public_and_skips_database_when_configured(self) -> None:
        response = self.client.get("/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ready",
                "database": "skipped",
                "explanation_load_mode": "lazy",
            },
        )

    def test_api_key_is_required(self) -> None:
        response = self.client.get("/folders")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid API key."})

    def test_folder_response_contracts_and_partial_update(self) -> None:
        create_response = self.client.post(
            "/folders",
            headers=self.headers,
            json={"name": "Personal", "description": "Daily notes"},
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(
            set(create_response.json()),
            {"folder_id", "name", "created_at"},
        )

        list_response = self.client.get("/folders", headers=self.headers)
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(
            set(list_response.json()[0]),
            {"folder_id", "name", "last_open_at"},
        )

        open_response = self.client.patch(
            f"/folders/{FOLDER_ID}/open",
            headers=self.headers,
        )
        self.assertEqual(open_response.status_code, 200)
        self.assertEqual(set(open_response.json()), {"folder_id", "last_open_at"})

        update_name_response = self.client.patch(
            f"/folders/{FOLDER_ID}",
            headers=self.headers,
            json={"name": "Updated"},
        )
        self.assertEqual(update_name_response.status_code, 200)
        self.assertEqual(
            self.app.state.folder_service.update_calls[-1],
            {"name": "Updated", "description": None, "update_description": False},
        )

        update_description_response = self.client.patch(
            f"/folders/{FOLDER_ID}",
            headers=self.headers,
            json={"description": "Updated description"},
        )
        self.assertEqual(update_description_response.status_code, 200)
        self.assertEqual(
            self.app.state.folder_service.update_calls[-1],
            {
                "name": None,
                "description": "Updated description",
                "update_description": True,
            },
        )

    def test_note_response_contracts_accept_apostrophe_sentences(self) -> None:
        create_response = self.client.post(
            f"/folders/{FOLDER_ID}/notes",
            headers=self.headers,
            json={"sentence": "I'm learning how to make pizza."},
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(
            set(create_response.json()),
            {"note_id", "folder_id", "sentence", "created_at"},
        )

        list_response = self.client.get(
            f"/folders/{FOLDER_ID}/notes",
            headers=self.headers,
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(set(list_response.json()[0]), {"note_id", "sentence"})

        detail_response = self.client.get(
            f"/folders/{FOLDER_ID}/notes/{NOTE_1_ID}",
            headers=self.headers,
        )
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(
            set(detail_response.json()),
            {"note_id", "folder_id", "sentence", "created_at", "updated_at"},
        )

        update_response = self.client.put(
            f"/folders/{FOLDER_ID}/notes/{NOTE_1_ID}",
            headers=self.headers,
            json={"sentence": "I'm still learning how to make pizza."},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(
            set(update_response.json()),
            {"note_id", "folder_id", "sentence", "updated_at"},
        )

    def test_relation_and_explanation_contracts(self) -> None:
        relations_response = self.client.get(
            f"/folders/{FOLDER_ID}/relations",
            headers=self.headers,
        )
        self.assertEqual(relations_response.status_code, 200)
        self.assertEqual(
            set(relations_response.json()[0]),
            {
                "relation_id",
                "note_1_id",
                "note_1_sentence",
                "note_2_id",
                "note_2_sentence",
            },
        )

        evidence_response = self.client.get(
            f"/folders/{FOLDER_ID}/relations/{RELATION_ID}/evidence",
            headers=self.headers,
        )
        self.assertEqual(evidence_response.status_code, 200)
        self.assertEqual(
            set(evidence_response.json()),
            {
                "relation_id",
                "relation_type",
                "similarity_score",
                "nli_label",
                "words_overlap",
                "similar_words",
            },
        )

        missing_response = self.client.get(
            f"/folders/{FOLDER_ID}/relations/{RELATION_ID}/explanation",
            headers=self.headers,
        )
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(missing_response.json(), {"detail": "Explanation not found."})

        create_response = self.client.post(
            f"/folders/{FOLDER_ID}/relations/{RELATION_ID}/explanation",
            headers=self.headers,
        )
        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(set(create_response.json()), {"relation_id", "explanation"})

        repeat_response = self.client.post(
            f"/folders/{FOLDER_ID}/relations/{RELATION_ID}/explanation",
            headers=self.headers,
        )
        self.assertEqual(repeat_response.status_code, 200)
        self.assertEqual(repeat_response.json(), create_response.json())

        get_response = self.client.get(
            f"/folders/{FOLDER_ID}/relations/{RELATION_ID}/explanation",
            headers=self.headers,
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json(), create_response.json())


if __name__ == "__main__":
    unittest.main()
