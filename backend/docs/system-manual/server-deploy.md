# Internal Server Deploy Guide

This guide describes the current supported deployment target: an internal
Ubuntu server, no public internet exposure, no sudo requirement, and `nohup` as
the temporary process runner.

## Target

```text
Mode: internal/private API
Host: 127.0.0.1
Port: 6550
Process runner: nohup
Reverse proxy: not required for current target
sudo: not required
```

Future public deployment may add nginx, TLS, systemd, and stronger monitoring.
Those are outside the current internal/nohup target.

## Files To Upload

Minimal deploy package:

```text
backend/
  main.py
  requirements.txt
  .env.example
  src/
  scripts/
  tests/
```

Useful optional files:

```text
backend/database/
backend/docs/
README.md
```

`backend/database/` contains SQL files that the developer or server admin can
run manually when preparing the database. The application and deploy scripts do
not apply schema or indexes automatically.

Do not upload a local `.env` containing real development secrets. Create
`backend/.env` directly on the server.

## Required Script Set

```text
backend/scripts/
  check_deploy_ready.py
  check_db_ready.py
  run_server.sh
  start_nohup.sh
  stop_nohup.sh
```

Remove old demo/integration scripts from the server package unless they are
needed for a specific manual test.

## Server Environment

Create `.env`:

```bash
cd backend
cp .env.example .env
nano .env
```

Recommended internal/nohup values:

```env
APP_ENV=production
APP_HOST=127.0.0.1
APP_PORT=6550
ENABLE_DOCS=false
READY_CHECK_DATABASE=true

LOG_LEVEL=INFO
LOG_REQUESTS=true
SLOW_REQUEST_MS=3000

API_SECRET_KEY=your-real-secret
API_KEY_HEADER_NAME=X-API-Key

DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=your-db
DB_USER=your-user
DB_PASSWORD=your-password
DB_CONNECT_TIMEOUT=10

EXPLANATION_LOAD_MODE=lazy

TOKENIZERS_PARALLELISM=false
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

Notes:

- `APP_PORT=6550` makes `run_server.sh` and `start_nohup.sh` use port `6550`.
- `ENABLE_DOCS=false` disables Swagger/OpenAPI in production mode.
- `READY_CHECK_DATABASE=true` makes `/ready` check DB connectivity.
- `EXPLANATION_LOAD_MODE=lazy` reduces long-lived memory use on small servers.

## Config Values You Can Change

These values are read from `backend/.env` when the server starts. After changing
them, restart the API with `stop_nohup.sh` and `start_nohup.sh`.

### App Runtime

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `APP_ENV` | `production` | any label such as `development`, `staging` | Environment label for runtime checks/log context. |
| `APP_HOST` | `127.0.0.1` | another bind host, only if server policy allows | Controls where uvicorn listens. Keep `127.0.0.1` for internal/private mode. |
| `APP_PORT` | `6550` | any free TCP port, for example `8000` | Changes the API port used by `run_server.sh` and `start_nohup.sh`. |
| `ENABLE_DOCS` | `false` | `true`, `false` | `true` enables `/docs` and `/openapi.json`; keep `false` for production/internal server. |
| `READY_CHECK_DATABASE` | `true` | `true`, `false` | `true` makes `/ready` verify DB connectivity; `false` only checks app runtime readiness. |

### Logging

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | Controls application log verbosity. Use `DEBUG` only for short troubleshooting windows. |
| `LOG_REQUESTS` | `true` | `true`, `false` | Enables request logs with method, path, status, and duration. |
| `SLOW_REQUEST_MS` | `3000` | positive integer milliseconds | Requests slower than this threshold are logged as slow requests. Increase if AI requests are expected to take longer. |

### Database

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `DB_HOST` | `127.0.0.1` | database host/IP | PostgreSQL host. |
| `DB_PORT` | `5432` | configured PostgreSQL port | PostgreSQL port. |
| `DB_NAME` | server DB name | any existing DB name | Database used by the backend. Must match prepared schema. |
| `DB_USER` | server DB user | any valid DB user | User used by psycopg3 connections. |
| `DB_PASSWORD` | secret value | valid DB password | Password for `DB_USER`. Do not commit. |
| `DB_CONNECT_TIMEOUT` | `10` | positive integer seconds | Maximum connection wait time before DB connection fails. |
| `DATABASE_URL` | optional | full PostgreSQL connection URL | If set, it is used instead of individual host/port/name/user/password values. |

### API Security

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `API_SECRET_KEY` | real secret | any strong secret string | Required value for protected endpoints. Rotate if leaked. |
| `API_KEY_HEADER_NAME` | `X-API-Key` | another header name | Changes which request header carries the API key. Client requests must match. |

### AI Models And Pipeline

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `EMBEDDING_MODEL` | `sentence-transformers/all-mpnet-base-v2` | compatible sentence-transformers model | Changes embedding model. `EMBEDDING_DIMENSION` and DB vector dimension must match. |
| `EMBEDDING_DIMENSION` | `768` | dimension of selected embedding model | Must match both model output and database vector column. |
| `NLI_MODEL` | `cross-encoder/nli-deberta-v3-base` | compatible cross-encoder NLI model | Changes relation classification model. |
| `EXPLANATION_MODEL` | `Qwen/Qwen3-0.6B` | compatible Hugging Face text generation model | Changes explanation generator model. May change memory and latency. |
| `EXPLANATION_MAX_NEW_TOKENS` | `128` | positive integer | Maximum generated explanation length. Higher values may increase latency and memory use. |
| `EXPLANATION_LOAD_MODE` | `lazy` | `lazy`, `startup` | `lazy` loads/unloads during explanation POST; `startup` keeps model loaded after startup. |

### Similarity Thresholds

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `SIMILARITY_THRESHOLD` | `0.40` | float between 0 and 1 | Minimum similarity score for candidate relations. Higher means fewer relations. |
| `THRESHOLD_SCALE` | `0.20` | non-negative float | Additional threshold scaling used by relation rules. |
| `SIMILARITY_TOP_K` | `10` | positive integer | Number of nearest notes to inspect per note. Higher may increase DB/model work. |
| `SIMILAR_WORD_THRESHOLD` | `0.55` | float between 0 and 1 | Minimum similar-word score stored in evidence. |

### Runtime Resource Limits

| Config | Typical Value | Other Valid Values | Effect |
| --- | --- | --- | --- |
| `TOKENIZERS_PARALLELISM` | `false` | `true`, `false` | Keep `false` on small servers to reduce noisy tokenizer parallelism behavior. |
| `OMP_NUM_THREADS` | `1` | positive integer | Limits OpenMP thread usage. Higher may increase CPU parallelism and RAM pressure. |
| `MKL_NUM_THREADS` | `1` | positive integer | Limits MKL thread usage. Higher may increase CPU parallelism and RAM pressure. |

## Dependency Setup

If the server can install packages from an approved source:

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

If the server cannot access package sources, prepare a compatible `.venv` or
wheelhouse on another machine with the same Python/OS compatibility and copy it
to the server.

## Database Preparation

The database must already exist and match `backend/database/er_diagram.dbml`.
SQL setup files are stored in `backend/database/`:

```text
create_extension.sql
create_table.sql
create_index.sql
er_diagram.dbml
```

These SQL files must be run manually on the server by someone with the correct
database privileges. The backend application does not apply them. See
[File Structure](file-structure.md#database-files) for each file's purpose and
[Database Detail](database-detail.md) for table, extension, relationship, and
index details.

## Pre-Start Checks

Run these from the server package before starting the API:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
.venv/bin/python -m unittest discover -s tests
```

Expected:

```text
check_deploy_ready.py: PASS
check_db_ready.py: PASS DB readiness check passed
unit tests: Ran 25 tests, OK
```

If a check fails, fix that item before starting the service.

## Start The API With nohup

```bash
cd backend
bash scripts/start_nohup.sh
```

Check the process:

```bash
cat runtime/noteconnect.pid
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
```

Check the log:

```bash
tail -n 100 runtime/noteconnect.log
```

Expected:

- `runtime/noteconnect.pid` exists.
- `runtime/noteconnect.log` exists.
- uvicorn runs on `127.0.0.1:6550`.
- no startup traceback appears.

## Health And Readiness

```bash
curl http://127.0.0.1:6550/health
curl http://127.0.0.1:6550/ready
```

Expected:

```json
{"status":"ok"}
```

```json
{
  "status": "ready",
  "database": "ok",
  "explanation_load_mode": "lazy"
}
```

## Authentication Check

Protected endpoints should reject missing or wrong API keys:

```bash
curl -i http://127.0.0.1:6550/folders
curl -i http://127.0.0.1:6550/folders -H "X-API-Key: wrong-key"
```

Expected:

```text
401 Unauthorized
```

## Functional Smoke Test

Set variables:

```bash
API=http://127.0.0.1:6550
KEY=your-real-secret
```

Create a folder:

```bash
curl -s -X POST "$API/folders" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"SERVER_TEST\",\"description\":\"deploy smoke test\"}"
```

Create two related notes:

```bash
curl -s -X POST "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pizza.\"}"

curl -s -X POST "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I am studying pizza cooking.\"}"
```

List relations and evidence:

```bash
curl -s "$API/folders/<folder_id>/relations" \
  -H "X-API-Key: $KEY"

curl -s "$API/folders/<folder_id>/relations/<relation_id>/evidence" \
  -H "X-API-Key: $KEY"
```

Check explanation behavior:

```bash
curl -i "$API/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: $KEY"

curl -i -X POST "$API/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: $KEY"

curl -i -X POST "$API/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: $KEY"
```

Expected:

- `GET /explanation` returns existing explanation or `404` before generation.
- first `POST /explanation` generates and stores explanation.
- repeated `POST /explanation` returns the existing explanation.
- process remains alive after AI requests.

## Restart And Recovery

```bash
cd backend
bash scripts/stop_nohup.sh
bash scripts/start_nohup.sh
curl http://127.0.0.1:6550/ready
curl http://127.0.0.1:6550/folders -H "X-API-Key: your-real-secret"
```

Expected:

- `/ready` returns `database: ok`.
- existing DB data is still readable.
- no startup traceback appears in `runtime/noteconnect.log`.

## Cleanup Test Data

```bash
curl -i -X DELETE "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY"

curl -s "$API/folders" \
  -H "X-API-Key: $KEY"
```

Expected:

- test folder disappears from active folder lists.
- rows are soft deleted through `deleted_at`.

## Stop Service

```bash
cd backend
bash scripts/stop_nohup.sh
```

Expected:

- process stops.
- `runtime/noteconnect.pid` is removed.

## Memory Checks

Check memory before start, after `/ready`, and after AI workflows:

```bash
free -h
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
```

Latest validated server behavior:

```text
check_deploy_ready.py passed
check_db_ready.py passed
unit tests passed: Ran 25 tests, OK
/health returned ok
/ready returned database: ok
nohup start/stop worked
API CRUD passed
relation/evidence creation passed
explanation POST and repeated POST passed
process stayed alive
swap did not grow abnormally
no critical traceback appeared for tested flows
Phase 5 deploy package passed server verification
```

## Acceptance Checklist

```text
[ ] backend/.env exists on the server
[ ] APP_HOST=127.0.0.1
[ ] APP_PORT=6550
[ ] ENABLE_DOCS=false
[ ] READY_CHECK_DATABASE=true
[ ] LOG_REQUESTS=true
[ ] SLOW_REQUEST_MS is set
[ ] EXPLANATION_LOAD_MODE=lazy
[ ] API_SECRET_KEY is configured
[ ] database SQL files were handled manually by the responsible developer/admin
[ ] check_deploy_ready.py passes
[ ] check_db_ready.py passes
[ ] unit tests pass: Ran 25 tests, OK
[ ] nohup start creates runtime/noteconnect.pid
[ ] /health returns ok
[ ] /ready returns database: ok
[ ] missing/wrong API key returns 401
[ ] folder/note CRUD smoke test passes
[ ] relation/evidence smoke test passes
[ ] explanation POST passes
[ ] repeated explanation POST returns existing explanation
[ ] restart/recovery test passes
[ ] cleanup soft delete behavior passes
[ ] nohup stop removes PID file and process exits
[ ] runtime/noteconnect.log has no critical traceback for tested flows
[ ] RAM/swap remains acceptable for the tested workload
```
