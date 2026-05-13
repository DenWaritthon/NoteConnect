# Backend Test Detail

This document explains the current backend test strategy, what each test file
checks, how to run tests locally or on the server, and the latest verified
result.

## Test Strategy

The current production-safe test set has two layers:

| Layer | Purpose | Uses Real DB | Loads AI Models |
| --- | --- | --- | --- |
| Fast unit/API tests | Verify API contracts, service rules, config, scripts, and repository SQL contracts. | No | No |
| Server readiness checks | Verify deploy config, imports, package availability, DB connectivity, and local model readiness. | Connectivity only | `check_model_ready.py` loads models |

This keeps tests safe to run on the production server before or after `nohup`
deployment.

Phase 1-3 real DB/model integration checks were completed successfully during
development. The detailed development and verification notes live in
`backend/docs/progrest/`:

- [Phase 1](../progrest/phase-1.md)
- [Phase 2](../progrest/phase-2.md)
- [Phase 3](../progrest/phase-3.md)

Those heavier integration scripts are not part of the minimal server deploy
package because the current server package should stay small and safe.

## Commands

Run compile check:

```bash
cd backend
.venv/bin/python -m compileall src main.py scripts tests
```

Run fast tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

Run server readiness checks:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
.venv/bin/python scripts/check_model_ready.py
```

Expected current result:

```text
compileall: PASS
unit tests: Ran 32 tests, OK
check_deploy_ready.py: PASS
check_db_ready.py: PASS
check_model_ready.py: PASS
```

## Test Files

```text
backend/tests/
  test_api_contract.py
  test_operability.py
  test_repository_contract.py
  test_runtime_config.py
  test_service_pipeline.py
```

## test_api_contract.py

Technique:

- Uses FastAPI `TestClient`.
- Replaces production services with fake in-memory services.
- Verifies HTTP behavior without PostgreSQL and without AI models.

Coverage:

| Area | Checks |
| --- | --- |
| Health/readiness | `GET /health` is public; `/ready` reports DB and model readiness fields. |
| Auth | Protected endpoints reject missing API keys with `401`. |
| Folder API | Create, list, open, partial update by name, partial update by description. |
| Note API | Create, list, get, update, and apostrophe-safe sentences such as `I'm`. |
| Relation API | List relations and get latest evidence response shape. |
| Explanation API | Missing `GET` returns `404`; first `POST` returns `201`; repeated `POST` returns `200`; later `GET` returns stored explanation. |

Why it matters:

- Confirms frontend/API contract stability.
- Prevents regressions in response shape.
- Confirms route methods match intended API usage.

## test_runtime_config.py

Technique:

- Uses controlled environment variables.
- Creates app instances with different runtime settings.
- Mocks DB readiness failure paths.

Coverage:

| Area | Checks |
| --- | --- |
| Config loading | `.env`/environment values map into `AppConfig`. |
| Explanation mode | Invalid `EXPLANATION_LOAD_MODE` fails fast. |
| Database config | connection kwargs include `connect_timeout`. |
| Docs disabling | `ENABLE_DOCS=false` disables `/docs` and `/openapi.json`. |
| Readiness | `/ready` reports loaded/lazy model status and returns `503` when DB or model readiness fails. |

## test_operability.py

Technique:

- Reads script/config files as text.
- Runs readiness script functions with mocked dependencies.
- Avoids starting uvicorn or opening real DB connections.

Coverage:

| Area | Checks |
| --- | --- |
| Server command | `run_server.sh` uses one worker and does not enable reload. |
| Env loading | `run_server.sh` sources `backend/.env`, so `APP_PORT=6550` applies. |
| Model files | Local model readiness detects missing paths and Git LFS pointer weights. |
| Model script | `check_model_ready.py` returns non-zero when model files are not ready. |
| nohup mode | `start_nohup.sh` and `stop_nohup.sh` use `runtime/noteconnect.pid` and `runtime/noteconnect.log`. |
| Deploy readiness | `check_deploy_ready.py` reports expected runtime settings including logging config. |
| DB readiness | `check_db_ready.py` returns `0` on success and `1` on failure. |
| Index baseline | `backend/database/create_index.sql` contains expected baseline index names. |
| Logging | known log levels are accepted. |

## test_repository_contract.py

Technique:

- Static source check for repository SQL.
- No database connection.

Coverage:

| Area | Checks |
| --- | --- |
| Current table names | Repository SQL references `noteconnect_folder`, `noteconnect_note`, `noteconnect_note_relation`, and `noteconnect_note_relation_evidence`. |
| Old table names | Repository SQL does not reference previous table names in SQL statements. |

Why it matters:

- Catches accidental drift from `backend/database/er_diagram.dbml`.

## test_service_pipeline.py

Technique:

- Uses fake repositories and fake model objects.
- Tests service behavior without database/model startup.

Coverage:

| Area | Checks |
| --- | --- |
| Relation evidence | New evidence uses the required `llm_payload` keys: `note_1`, `note_2`, `system_prompt`, `question_prompt`. |
| Process status | New relation starts with `relation_confirmed`. |
| Explanation create | Loads from `llm_payload`, stores explanation, updates status to `add_explanation`. |
| Explanation get | Does not generate or write when explanation is missing. |
| Lazy generator | Lazy explanation mode loads and unloads around generation. |

## Readiness Scripts

### check_deploy_ready.py

Checks:

- Python/app config can be loaded.
- required package imports are available.
- production settings are visible.
- `main:app` can be imported.
- logging settings such as `LOG_REQUESTS` and `SLOW_REQUEST_MS` are reported.

It does not connect to PostgreSQL. Unit tests mock model loading, while the
server-side `check_model_ready.py` command can load real local models before
starting the API.

### check_db_ready.py

Checks:

- configured PostgreSQL database is reachable through the same DB helper used
  by the app.

It does not write application rows and does not run migrations.

### check_model_ready.py

Checks:

- configured embedding, NLI, and explanation model paths exist
- local model directories contain weight files
- weight files are not Git LFS pointer stubs
- models can load with local files only

Use `--skip-load` for a quick file-only check:

```bash
.venv/bin/python scripts/check_model_ready.py --skip-load
```

The full check is recommended before starting the service:

```bash
.venv/bin/python scripts/check_model_ready.py
```

## Server Smoke Tests

After starting with `nohup`, verify:

```bash
curl http://127.0.0.1:6550/health
curl http://127.0.0.1:6550/ready
```

Then run a small API workflow:

1. Missing/wrong API key returns `401`.
2. Create folder.
3. Create two related notes.
4. List notes.
5. List relations.
6. Get relation evidence.
7. `GET /explanation` returns existing explanation or `404`.
8. `POST /explanation` generates once.
9. Repeated `POST /explanation` returns existing explanation.
10. Delete test folder and confirm it disappears from active list.
11. Restart `nohup` and confirm `/ready` still passes.

## Latest Verified Result

Latest local/server validation:

```text
Deploy readiness checks: PASS
DB readiness check: PASS
Fast tests: 32 passed
Phase 5 server deploy verification: PASS
Offline model readiness check: PASS
Phase 1-3 DB/model integration checks: PASS
```

Latest server smoke coverage passed:

```text
/health ok
/ready database: ready and model_verified_loadable: true
nohup start/stop ok
API CRUD ok
create note first request did not kill process
relation/evidence created
explanation POST passed
repeated POST did not regenerate
restart/recovery passed
auth/bad request checks passed
cleanup soft delete passed
swap did not grow abnormally
no critical traceback in tested flows
```

## Interpreting Warnings

Non-failing messages that may appear:

- Hugging Face may warn about unauthenticated requests when no `HF_TOKEN` is set.
- Model load may print compatibility warnings during startup.
- Request logs may show `INFO` or slow-request `WARNING` lines when
  `LOG_REQUESTS=true`.

Failing signs:

- traceback that aborts startup.
- `/ready` returns `503` when DB is expected to be reachable.
- `nohup` process exits unexpectedly.
- repeated explanation `POST` generates new text instead of returning stored text.
- unit test count or failures change unexpectedly without an intentional code update.
