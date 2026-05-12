"""Run a real Phase 1-3 integration test against the configured database.

This script uses the FastAPI app with its real lifespan so the same services,
model startup path, repositories, and PostgreSQL database are exercised. It
creates a uniquely named folder and soft deletes it during cleanup.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import app
from src.core.config import get_config
from src.core.database import transaction


REQUIRED_LLM_PAYLOAD_KEYS = {"note_1", "note_2", "system_prompt", "question_prompt"}


class IntegrationCheckError(RuntimeError):
    """Raised when a real integration check fails."""


def assert_status(response, expected_status: int, label: str) -> dict[str, Any]:
    if response.status_code != expected_status:
        raise IntegrationCheckError(
            f"{label}: expected {expected_status}, got {response.status_code}: "
            f"{response.text}"
        )
    if response.content:
        return response.json()
    return {}


def assert_keys(payload: dict[str, Any], expected_keys: set[str], label: str) -> None:
    actual_keys = set(payload)
    if actual_keys != expected_keys:
        raise IntegrationCheckError(
            f"{label}: expected keys {sorted(expected_keys)}, got {sorted(actual_keys)}"
        )


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch_db_state(folder_id: UUID, relation_id: UUID | None = None) -> dict[str, Any]:
    with transaction() as connection:
        folder = connection.execute(
            """
            SELECT folder_id, deleted_at
            FROM noteconnect_folder
            WHERE folder_id = %s
            """,
            (folder_id,),
        ).fetchone()
        notes = connection.execute(
            """
            SELECT note_id, sentence_embedding IS NOT NULL AS has_embedding, deleted_at
            FROM noteconnect_note
            WHERE folder_id = %s
            ORDER BY created_at ASC
            """,
            (folder_id,),
        ).fetchall()
        relations = connection.execute(
            """
            SELECT relation_id, process_status, deleted_at
            FROM noteconnect_note_relation
            WHERE folder_id = %s
            ORDER BY created_at ASC
            """,
            (folder_id,),
        ).fetchall()

        evidence = None
        if relation_id is not None:
            evidence = connection.execute(
                """
                SELECT explanation, llm_payload, deleted_at
                FROM noteconnect_note_relation_evidence
                WHERE relation_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (relation_id,),
            ).fetchone()

    return {
        "folder": folder,
        "notes": notes,
        "relations": relations,
        "evidence": evidence,
    }


def main() -> None:
    config = get_config()
    if not config.api_secret_key:
        raise IntegrationCheckError("API_SECRET_KEY is required for API testing.")

    headers = {config.api_key_header_name: config.api_secret_key}
    test_suffix = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    folder_name = f"TEST_PHASE_1_3_{test_suffix}"
    folder_id: UUID | None = None
    relation_id: UUID | None = None

    passed: list[str] = []

    def mark(label: str) -> None:
        passed.append(label)
        print(f"PASS {label}")

    with TestClient(app) as client:
        health = assert_status(client.get("/health"), 200, "health")
        if health != {"status": "ok"}:
            raise IntegrationCheckError(f"health: unexpected payload {health}")
        mark("P2 health endpoint")

        unauthorized = assert_status(
            client.get("/folders"),
            401,
            "api key rejection",
        )
        if unauthorized != {"detail": "Invalid API key."}:
            raise IntegrationCheckError(
                f"api key rejection: unexpected payload {unauthorized}"
            )
        mark("P2 API key rejection")

        folder = assert_status(
            client.post(
                "/folders",
                headers=headers,
                json={"name": folder_name, "description": "Real integration test"},
            ),
            201,
            "create folder",
        )
        assert_keys(folder, {"folder_id", "name", "created_at"}, "create folder")
        folder_id = UUID(folder["folder_id"])
        mark("P1/P2 create folder")

        folder_detail = assert_status(
            client.get(f"/folders/{folder_id}", headers=headers),
            200,
            "get folder",
        )
        updated_at_before_open = parse_datetime(folder_detail["updated_at"])
        assert_keys(
            folder_detail,
            {
                "folder_id",
                "name",
                "description",
                "created_at",
                "updated_at",
                "last_open_at",
            },
            "get folder",
        )
        mark("P2 get folder contract")

        patch_name = assert_status(
            client.patch(
                f"/folders/{folder_id}",
                headers=headers,
                json={"name": f"{folder_name}_UPDATED"},
            ),
            200,
            "patch folder name",
        )
        if patch_name["name"] != f"{folder_name}_UPDATED":
            raise IntegrationCheckError("patch folder name did not update name")
        mark("P2 patch folder with name only")

        patch_description = assert_status(
            client.patch(
                f"/folders/{folder_id}",
                headers=headers,
                json={"description": "Description only update"},
            ),
            200,
            "patch folder description",
        )
        if patch_description["description"] != "Description only update":
            raise IntegrationCheckError(
                "patch folder description did not update description"
            )
        mark("P2 patch folder with description only")

        opened = assert_status(
            client.patch(f"/folders/{folder_id}/open", headers=headers),
            200,
            "open folder",
        )
        assert_keys(opened, {"folder_id", "last_open_at"}, "open folder")
        folder_after_open = assert_status(
            client.get(f"/folders/{folder_id}", headers=headers),
            200,
            "get folder after open",
        )
        patched_updated_at = parse_datetime(patch_description["updated_at"])
        if parse_datetime(folder_after_open["updated_at"]) != patched_updated_at:
            raise IntegrationCheckError("open folder changed updated_at")
        if parse_datetime(folder_after_open["updated_at"]) == updated_at_before_open:
            raise IntegrationCheckError("folder metadata updates did not change updated_at")
        mark("P2 open folder updates last_open_at only")

        note_1 = assert_status(
            client.post(
                f"/folders/{folder_id}/notes",
                headers=headers,
                json={"sentence": "I'm learning how to make pizza."},
            ),
            201,
            "create note 1",
        )
        assert_keys(note_1, {"note_id", "folder_id", "sentence", "created_at"}, "note 1")
        note_1_id = UUID(note_1["note_id"])
        mark("P1/P2 create note with apostrophe")

        note_1_update = assert_status(
            client.put(
                f"/folders/{folder_id}/notes/{note_1_id}",
                headers=headers,
                json={"sentence": "I'm learning how to make pizza dough."},
            ),
            200,
            "update note 1",
        )
        assert_keys(
            note_1_update,
            {"note_id", "folder_id", "sentence", "updated_at"},
            "update note 1",
        )
        mark("P1/P2 update note with apostrophe")

        note_2 = assert_status(
            client.post(
                f"/folders/{folder_id}/notes",
                headers=headers,
                json={"sentence": "I am learning to prepare pizza dough."},
            ),
            201,
            "create note 2",
        )
        note_2_id = UUID(note_2["note_id"])
        mark("P1/P2 create related noteconnect_note")

        notes = assert_status(
            client.get(f"/folders/{folder_id}/notes", headers=headers),
            200,
            "list notes",
        )
        if {UUID(noteconnect_note["note_id"]) for note in notes} != {note_1_id, note_2_id}:
            raise IntegrationCheckError("list notes did not return both test notes")
        assert_keys(notes[0], {"note_id", "sentence"}, "list notes")
        mark("P2 list notes contract")

        note_detail = assert_status(
            client.get(f"/folders/{folder_id}/notes/{note_1_id}", headers=headers),
            200,
            "get noteconnect_note",
        )
        assert_keys(
            note_detail,
            {"note_id", "folder_id", "sentence", "created_at", "updated_at"},
            "get noteconnect_note",
        )
        mark("P2 get note contract")

        relations = assert_status(
            client.get(f"/folders/{folder_id}/relations", headers=headers),
            200,
            "list relations",
        )
        if not relations:
            raise IntegrationCheckError("list relations returned no relations")
        assert_keys(
            relations[0],
            {
                "relation_id",
                "note_1_id",
                "note_1_sentence",
                "note_2_id",
                "note_2_sentence",
            },
            "list relations",
        )
        relation_id = UUID(relations[0]["relation_id"])
        mark("P1/P2 relation created and listed")

        evidence = assert_status(
            client.get(
                f"/folders/{folder_id}/relations/{relation_id}/evidence",
                headers=headers,
            ),
            200,
            "get relation evidence",
        )
        assert_keys(
            evidence,
            {
                "relation_id",
                "relation_type",
                "similarity_score",
                "nli_label",
                "words_overlap",
                "similar_words",
            },
            "get relation evidence",
        )
        mark("P1/P2 relation evidence contract")

        state_before_explanation = fetch_db_state(folder_id, relation_id)
        if not all(noteconnect_note["has_embedding"] for note in state_before_explanation["notes"]):
            raise IntegrationCheckError("one or more notes did not save embeddings")
        if not state_before_explanation["evidence"]:
            raise IntegrationCheckError("relation evidence was not saved")
        llm_payload = state_before_explanation["evidence"]["llm_payload"]
        if set(llm_payload) != REQUIRED_LLM_PAYLOAD_KEYS:
            raise IntegrationCheckError(
                "llm_payload keys mismatch: "
                f"expected {sorted(REQUIRED_LLM_PAYLOAD_KEYS)}, "
                f"got {sorted(llm_payload)}"
            )
        if state_before_explanation["relations"][0]["process_status"] != "relation_confirmed":
            raise IntegrationCheckError("initial relation process_status mismatch")
        mark("P1 DB embedding, evidence, llm_payload, and status verification")

        missing_explanation = assert_status(
            client.get(
                f"/folders/{folder_id}/relations/{relation_id}/explanation",
                headers=headers,
            ),
            404,
            "missing explanation",
        )
        if missing_explanation != {"detail": "Explanation not found."}:
            raise IntegrationCheckError(
                f"missing explanation: unexpected payload {missing_explanation}"
            )
        mark("P3 GET explanation missing returns 404")

        created_explanation = assert_status(
            client.post(
                f"/folders/{folder_id}/relations/{relation_id}/explanation",
                headers=headers,
            ),
            201,
            "create explanation",
        )
        assert_keys(created_explanation, {"relation_id", "explanation"}, "create explanation")
        if not created_explanation["explanation"].strip():
            raise IntegrationCheckError("created explanation is empty")
        mark("P3 POST explanation generates and returns 201")

        repeated_explanation = assert_status(
            client.post(
                f"/folders/{folder_id}/relations/{relation_id}/explanation",
                headers=headers,
            ),
            200,
            "repeat explanation",
        )
        if repeated_explanation != created_explanation:
            raise IntegrationCheckError("repeat POST did not return existing explanation")
        mark("P3 repeated POST explanation returns existing 200")

        fetched_explanation = assert_status(
            client.get(
                f"/folders/{folder_id}/relations/{relation_id}/explanation",
                headers=headers,
            ),
            200,
            "get explanation after create",
        )
        if fetched_explanation != created_explanation:
            raise IntegrationCheckError("GET explanation did not return stored explanation")
        mark("P3 GET explanation after generation returns stored data")

        state_after_explanation = fetch_db_state(folder_id, relation_id)
        saved_explanation = state_after_explanation["evidence"]["explanation"]
        if saved_explanation != created_explanation["explanation"]:
            raise IntegrationCheckError("DB explanation does not match API response")
        relation_statuses = {
            relation["relation_id"]: relation["process_status"]
            for relation in state_after_explanation["relations"]
        }
        if relation_statuses[relation_id] != "add_explanation":
            raise IntegrationCheckError("relation process_status was not add_explanation")
        mark("P3 DB explanation and process_status verification")

        delete_response = assert_status(
            client.delete(f"/folders/{folder_id}", headers=headers),
            200,
            "cleanup folder",
        )
        if delete_response != {"deleted": True}:
            raise IntegrationCheckError(f"cleanup: unexpected payload {delete_response}")
        mark("P1 cleanup soft delete request")

    if folder_id is not None:
        cleanup_state = fetch_db_state(folder_id, relation_id)
        if cleanup_state["folder"]["deleted_at"] is None:
            raise IntegrationCheckError("cleanup did not soft delete folder")
        if not cleanup_state["notes"] or any(
            noteconnect_note["deleted_at"] is None for note in cleanup_state["notes"]
        ):
            raise IntegrationCheckError("cleanup did not soft delete notes")
        if not cleanup_state["relations"] or any(
            relation["deleted_at"] is None for relation in cleanup_state["relations"]
        ):
            raise IntegrationCheckError("cleanup did not soft delete relations")
        if cleanup_state["evidence"] and cleanup_state["evidence"]["deleted_at"] is None:
            raise IntegrationCheckError("cleanup did not soft delete evidence")
        mark("P1 DB soft delete cascade verification")

    print()
    print(f"Real integration checks passed: {len(passed)}")


if __name__ == "__main__":
    main()
