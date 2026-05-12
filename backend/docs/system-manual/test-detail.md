# Backend Test Detail

This document explains the current backend testing approach, the test scripts
that were added, how to run them, and what was verified for Phase 1-4 deploy
readiness.

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

### Server Deploy Readiness Checks

Server deploy checks are lightweight scripts that can be run on the production
server before starting the API.

Purpose:

- Verify the Python version, `.env`, production config, required packages, and
  `main:app` import.
- Verify the configured PostgreSQL database is reachable through the same
  database helper used by the application.
- Avoid writing application rows or loading AI models during server readiness
  checks.

Commands:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
```

### Development Integration Tests

Earlier Phase 1-3 development used a heavier real DB/model integration script to
verify the full workflow. That script is intentionally not part of the minimal
production server deploy package. The server package keeps only fast unit tests
and safe readiness scripts.

## Test Files

```text
backend/tests/
  __init__.py
  test_api_contract.py
  test_operability.py
  test_repository_contract.py
  test_runtime_config.py
  test_service_pipeline.py

backend/scripts/
  check_deploy_ready.py
  check_db_ready.py
  run_server.sh
  start_nohup.sh
  stop_nohup.sh
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

## `test_runtime_config.py`

This file tests production-oriented runtime configuration.

It verifies:

- `.env`/environment values map into `AppConfig`.
- invalid `EXPLANATION_LOAD_MODE` fails fast.
- database connection kwargs include `connect_timeout`.
- `ENABLE_DOCS=false` disables `/docs` and `/openapi.json`.
- `/ready` returns `503` when DB readiness is enabled and the DB check fails.

## `test_operability.py`

This file tests runtime and deploy scripts without starting uvicorn or opening a
real database connection.

It verifies:

- `run_server.sh` uses one worker and does not enable reload.
- `run_server.sh` sources `backend/.env` so settings such as `APP_PORT=6550`
  apply in foreground and `nohup` mode.
- `start_nohup.sh` and `stop_nohup.sh` use `runtime/noteconnect.pid` and
  `runtime/noteconnect.log`.
- `check_deploy_ready.py` reports expected production settings.
- `check_db_ready.py` returns `0` when the DB check succeeds and `1` when it
  fails.
- logging accepts configured log levels.

## `test_repository_contract.py`

This file statically checks repository SQL source files.

It verifies:

- repositories reference current DBML table names:
  - `noteconnect_folder`
  - `noteconnect_note`
  - `noteconnect_note_relation`
  - `noteconnect_note_relation_evidence`
- repositories do not reference previous table names in SQL statements.

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

Run server deploy readiness checks:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
```

## Historical Real Integration Coverage

The earlier Phase 1-3 real integration validation verified these checks before
the deploy package was trimmed:

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
Deploy readiness checks: PASS
DB readiness check: PASS
Fast tests: 23 passed
Historical real integration checks: 22 passed
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
