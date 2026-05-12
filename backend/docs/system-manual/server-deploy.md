# Internal Server Deploy Guide

This guide describes the current Phase 4 deployment target: run the backend on
an internal Ubuntu server with no public internet exposure and no sudo
requirement, using `nohup` as the process runner.

## Deployment Target

```text
Mode: internal/private API
Host binding: 127.0.0.1
Port: 6550
Process manager: nohup
Reverse proxy: not required for the current internal target
sudo: not required
```

The backend is expected to run from a copied deploy package, not necessarily
from a full git repository.

## Files To Upload

Minimal runtime and server-test package:

```text
backend/
  main.py
  requirements.txt
  .env.example
  src/
  scripts/
  tests/
```

The deploy script set should contain:

```text
backend/scripts/
  check_deploy_ready.py
  check_db_ready.py
  run_server.sh
  start_nohup.sh
  stop_nohup.sh
```

Do not upload real local secrets. Create `backend/.env` on the server.

## Server Environment

Create and edit `.env`:

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

`EXPLANATION_LOAD_MODE=lazy` avoids holding the explanation model in memory
between explanation requests. Embedding and NLI models are still initialized by
the main application service path.

## Dependency Setup

If the server can install from available package sources:

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

If the server cannot access package sources, prepare dependencies elsewhere and
copy a compatible `.venv` or wheelhouse according to the server Python and OS
environment.

## Pre-Start Checklist

Run these before starting the service:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
.venv/bin/python -m unittest discover -s tests
```

Expected results:

```text
check_deploy_ready.py: PASS for required settings, packages, and main:app import
check_db_ready.py: PASS DB readiness check passed
unit tests: Ran 23 tests, OK
```

If any readiness check returns `FAIL`, fix that item before starting the API.

## Start With nohup

```bash
cd backend
bash scripts/start_nohup.sh
```

Check the process and log:

```bash
cat runtime/noteconnect.pid
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
tail -n 50 runtime/noteconnect.log
```

## Runtime Health Checks

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

Protected endpoints should reject missing or wrong API keys:

```bash
curl -i http://127.0.0.1:6550/folders
curl -i http://127.0.0.1:6550/folders -H "X-API-Key: wrong-key"
```

Expected status:

```text
401 Unauthorized
```

## Functional Smoke Test

Use the real secret from `.env`:

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

Create notes:

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

Verify relation and evidence:

```bash
curl -s "$API/folders/<folder_id>/relations" \
  -H "X-API-Key: $KEY"

curl -s "$API/folders/<folder_id>/relations/<relation_id>/evidence" \
  -H "X-API-Key: $KEY"
```

Verify explanation behavior:

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
- repeated `POST /explanation` returns the existing explanation and does not
  regenerate.

## Restart And Recovery Test

```bash
cd backend
bash scripts/stop_nohup.sh
bash scripts/start_nohup.sh
curl http://127.0.0.1:6550/ready
curl http://127.0.0.1:6550/folders -H "X-API-Key: your-real-secret"
```

Expected:

- `/ready` returns `database: ok`.
- existing DB data remains readable.
- no startup traceback appears in `runtime/noteconnect.log`.

## Cleanup Test Data

```bash
curl -i -X DELETE "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY"

curl -s "$API/folders" \
  -H "X-API-Key: $KEY"
```

Expected:

- deleted test folder no longer appears in active folder lists.
- rows are soft deleted through `deleted_at`, not hard deleted.

## Stop Service

```bash
cd backend
bash scripts/stop_nohup.sh
```

Expected:

- process stops.
- `runtime/noteconnect.pid` is removed.

## Memory Checkpoints

Check memory before start, after ready, and after model workflows:

```bash
free -h
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
```

Latest server validation observed:

```text
Before start:
Mem total 7.8Gi, used 3.7Gi, available 4.0Gi, swap used 3.0Gi

Ready:
Mem total 7.8Gi, used 4.3Gi, available 3.5Gi, swap used 3.0Gi
Process RSS: 943464 KB
```

The tested server passed create note, relation/evidence, explanation generation,
repeated explanation POST, restart/recovery, auth/bad request, cleanup, and
nohup start/stop without significant swap growth or critical tracebacks.

## Internal/nohup Acceptance Checklist

Before marking a deploy ready:

```text
[ ] backend/.env exists and contains production/internal settings
[ ] APP_HOST=127.0.0.1
[ ] APP_PORT=6550
[ ] ENABLE_DOCS=false
[ ] READY_CHECK_DATABASE=true
[ ] EXPLANATION_LOAD_MODE=lazy
[ ] API_SECRET_KEY is configured
[ ] check_deploy_ready.py passes
[ ] check_db_ready.py passes
[ ] unit tests pass: Ran 23 tests, OK
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

## Current Phase 4 Completion Boundary

For this project, Phase 4 is complete when the backend can be deployed and
operated internally with `nohup`, pass the readiness checks above, and complete
the functional smoke workflow on the Ubuntu server.

Items such as nginx exposure, sudo-managed systemd services, public TLS,
connection pooling, heavy load testing, and advanced monitoring are future
hardening work beyond the current internal/nohup target.
