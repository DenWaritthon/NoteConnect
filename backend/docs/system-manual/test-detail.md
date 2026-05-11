# Backend Test Detail

This document explains the current backend testing approach, the test scripts
that were added, how to run them, and what was verified for Phase 1-3.

## Test Strategy

The backend now uses two complementary test layers.

### Fast Automated Tests

Fast tests use Python `unittest` and in-memory service doubles.

Purpose:

- Run quickly during development.
- Verify API response contracts without loading AI models.
- Verify service workflow rules without connecting to PostgreSQL.
- Avoid requiring extra test dependencies such as `pytest`.

Command:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

### Real Integration Test

The real integration test runs against the configured PostgreSQL database and
the real model lifecycle.

Purpose:

- Exercise the same FastAPI app and lifespan startup as production.
- Load the configured embedding, NLI, and explanation models.
- Write real folder, note, relation, and evidence rows to the database.
- Verify API behavior and database state together.
- Clean up test data through the soft delete folder flow.

Command:

```bash
cd backend
.venv/bin/python scripts/run_phase1_3_real_test.py
```

## Test Files

```text
backend/tests/
  __init__.py
  test_api_contract.py
  test_service_pipeline.py

backend/scripts/
  run_phase1_3_real_test.py
```

## `test_api_contract.py`

This file tests the API layer with FastAPI `TestClient` and fake services.

It verifies:

- `GET /health` is public and returns `{"status": "ok"}`.
- Protected endpoints reject missing API keys with `401`.
- Folder response contracts:
  - `POST /folders`
  - `GET /folders`
  - `PATCH /folders/{folder_id}/open`
  - `PATCH /folders/{folder_id}`
- Partial folder update behavior:
  - name only
  - description only
- Note response contracts:
  - `POST /folders/{folder_id}/notes`
  - `GET /folders/{folder_id}/notes`
  - `GET /folders/{folder_id}/notes/{note_id}`
  - `PUT /folders/{folder_id}/notes/{note_id}`
- Sentences containing apostrophes such as `I'm`.
- Relation response contracts:
  - `GET /folders/{folder_id}/relations`
  - `GET /folders/{folder_id}/relations/{relation_id}/evidence`
- Explanation API behavior:
  - missing `GET /explanation` returns `404`.
  - first `POST /explanation` returns `201`.
  - repeated `POST /explanation` returns `200`.
  - later `GET /explanation` returns the stored explanation.

This test intentionally avoids the real database and real models so it can be
run frequently.

## `test_service_pipeline.py`

This file tests service-layer behavior with fake repositories and fake model
objects.

It verifies:

- Newly created relation evidence uses the AGENTS.md `llm_payload` shape:
  - `note_1`
  - `note_2`
  - `system_prompt`
  - `question_prompt`
- New relations are created with `process_status = relation_confirmed`.
- `ExplanationService.create_explanation()`:
  - loads input from `llm_payload`.
  - stores the generated explanation on the latest evidence.
  - updates relation status to `add_explanation`.
- `ExplanationService.get_explanation()`:
  - does not generate explanation when none exists.
  - does not write to evidence when no explanation exists.

## `run_phase1_3_real_test.py`

This script is the milestone test for Phase 1-3.

It uses:

- the real FastAPI `app` from `backend/main.py`
- FastAPI `TestClient`
- real lifespan startup
- real `SentenceProcessor`
- real `ExplanationGenerator`
- real PostgreSQL connection from `.env`
- real repository SQL

The script creates a unique folder name:

```text
TEST_PHASE_1_3_<timestamp>
```

At the end, it deletes that folder through the API. Because the application
uses soft delete behavior, the rows remain in the database with `deleted_at`
set.

## How To Run All Tests

Run compile checks:

```bash
cd backend
.venv/bin/python -m compileall src main.py scripts tests
```

Run fast tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

Run real integration test:

```bash
cd backend
.venv/bin/python scripts/run_phase1_3_real_test.py
```

The real integration test requires:

- `backend/.env` configured.
- PostgreSQL reachable from the current machine.
- pgvector extension and schema already applied.
- model files available locally or network access to Hugging Face.
- enough time for model startup on first run.

## Real Integration Test Coverage

The real integration script verifies these checks:

```text
P2 health endpoint
P2 API key rejection
P1/P2 create folder
P2 get folder contract
P2 patch folder with name only
P2 patch folder with description only
P2 open folder updates last_open_at only
P1/P2 create note with apostrophe
P1/P2 update note with apostrophe
P1/P2 create related note
P2 list notes contract
P2 get note contract
P1/P2 relation created and listed
P1/P2 relation evidence contract
P1 DB embedding, evidence, llm_payload, and status verification
P3 GET explanation missing returns 404
P3 POST explanation generates and returns 201
P3 repeated POST explanation returns existing 200
P3 GET explanation after generation returns stored data
P3 DB explanation and process_status verification
P1 cleanup soft delete request
P1 DB soft delete cascade verification
```

## Latest Test Result

The latest completed run passed:

```text
Real integration checks passed: 22
```

Fast tests also passed:

```text
Ran 8 tests
OK
```

Observed non-failing runtime messages:

- Hugging Face may warn about unauthenticated requests when no `HF_TOKEN` is set.
- Model load reports may include unexpected `position_ids`; these were warnings
  during model loading and did not fail the test.

## Phase Completion Meaning

The Phase 1-3 progress is marked as `100%` because the following were verified:

- Phase 1 core DB pipeline writes notes, embeddings, relations, relation
  evidence, `llm_payload`, and soft delete state correctly.
- Phase 2 API endpoints return the expected response shapes and status codes.
- Phase 3 explanation workflow generates once, stores the explanation, returns
  existing explanation on repeated `POST`, supports read-only `GET`, and updates
  `process_status` to `add_explanation`.

Production hardening items such as load testing, deployment monitoring,
warmup policy, retry behavior, and performance tuning belong to Phase 4.
