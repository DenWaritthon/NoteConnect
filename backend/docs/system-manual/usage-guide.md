# Backend Usage Guide

This guide explains how to run and use the NoteConnect backend after local setup
or server deployment.

For endpoint-level request/response detail, see [API Reference](api-reference.md).
For server deployment steps, see [Server Deploy Guide](server-deploy.md).

## Prerequisites

- Python virtual environment exists at `backend/.venv`.
- PostgreSQL is available.
- pgvector is enabled in the database.
- Database schema matches `backend/database/er_diagram.dbml`.
- `backend/.env` exists and contains real environment values.

Database SQL files live in `backend/database/` and must be handled manually by
the developer/admin. The backend application does not apply schema or indexes.

## Environment Configuration

Use `backend/.env.example` as the reference.

Important values:

```env
APP_HOST=127.0.0.1
APP_PORT=6550
ENABLE_DOCS=false
READY_CHECK_DATABASE=true

DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=noteconnect
DB_USER=postgres
DB_PASSWORD=your-password
DB_CONNECT_TIMEOUT=10

API_SECRET_KEY=your-secret
API_KEY_HEADER_NAME=X-API-Key

LOG_LEVEL=INFO
LOG_REQUESTS=true
SLOW_REQUEST_MS=3000

EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
NLI_MODEL=cross-encoder/nli-deberta-v3-base
EXPLANATION_MODEL=Qwen/Qwen3-0.6B
EXPLANATION_MAX_NEW_TOKENS=128
EXPLANATION_LOAD_MODE=lazy
EMBEDDING_DIMENSION=768

SIMILARITY_THRESHOLD=0.40
THRESHOLD_SCALE=0.20
SIMILARITY_TOP_K=10
SIMILAR_WORD_THRESHOLD=0.55
```

Do not commit real `.env` secrets.

## Start Locally

Foreground run:

```bash
cd backend
bash scripts/run_server.sh
```

If `APP_PORT` is not changed, local development often uses:

```text
http://127.0.0.1:8000
```

If `.env` sets `APP_PORT=6550`, use:

```text
http://127.0.0.1:6550
```

## Start On Server With nohup

```bash
cd backend
bash scripts/start_nohup.sh
```

Check process:

```bash
cat runtime/noteconnect.pid
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
```

Check log:

```bash
tail -n 100 runtime/noteconnect.log
```

Stop:

```bash
cd backend
bash scripts/stop_nohup.sh
```

## Health And Readiness

```bash
curl "http://127.0.0.1:6550/health"
curl "http://127.0.0.1:6550/ready"
```

Expected health:

```json
{
  "status": "ok"
}
```

Expected ready:

```json
{
  "status": "ready",
  "database": "ok",
  "explanation_load_mode": "lazy"
}
```

`/health` means the process is alive. `/ready` means the app is ready and, when
enabled, can connect to the database.

## Basic API Workflow

Set variables:

```bash
API=http://127.0.0.1:6550
KEY=your-secret
```

### 1. Create Folder

```bash
curl -X POST "$API/folders" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Study Notes\",\"description\":\"Learning notes\"}"
```

Save the returned `folder_id`.

### 2. Open Folder

```bash
curl -X PATCH "$API/folders/<folder_id>/open" \
  -H "X-API-Key: $KEY"
```

This updates only `last_open_at`.

### 3. Create Notes

```bash
curl -X POST "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pizza.\"}"
```

```bash
curl -X POST "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I am studying pizza cooking.\"}"
```

Note creation may take time because embedding, similarity search, and NLI run
as part of the write workflow.

### 4. List Notes

```bash
curl "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY"
```

### 5. Update Note

```bash
curl -X PUT "$API/folders/<folder_id>/notes/<note_id>" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pasta.\"}"
```

Updating a note soft deletes active relations for that note and rebuilds new
relations from the updated sentence.

### 6. List Relations

```bash
curl "$API/folders/<folder_id>/relations" \
  -H "X-API-Key: $KEY"
```

### 7. Get Evidence

```bash
curl "$API/folders/<folder_id>/relations/<relation_id>/evidence" \
  -H "X-API-Key: $KEY"
```

### 8. Use Explanation

Read existing explanation:

```bash
curl "$API/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: $KEY"
```

If no explanation exists, `GET` returns `404` because it is read-only.

Create explanation once:

```bash
curl -X POST "$API/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: $KEY"
```

Repeated `POST` returns the stored explanation and does not regenerate it.

### 9. Delete Test Data

```bash
curl -X DELETE "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY"
```

Folder delete uses soft delete and also marks child notes, relations, and
evidence as deleted.

## Updating Folder Metadata

Update only name:

```bash
curl -X PATCH "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated Study Notes\"}"
```

Update only description:

```bash
curl -X PATCH "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"description\":\"I'm updating only the description.\"}"
```

Clear description:

```bash
curl -X PATCH "$API/folders/<folder_id>" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"description\":null}"
```

## Curl Quoting Notes

If JSON contains an apostrophe, do not wrap the whole JSON with single quotes:

```bash
# Avoid this when text contains I'm
-d '{"sentence":"I'm learning how to make pizza."}'
```

Use escaped double quotes:

```bash
-d "{\"sentence\":\"I'm learning how to make pizza.\"}"
```

Or use a JSON file:

```bash
curl -X POST "$API/folders/<folder_id>/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  --data @note.json
```

## Logs

Main server log:

```text
backend/runtime/noteconnect.log
```

PID file:

```text
backend/runtime/noteconnect.pid
```

Useful log meanings:

| Log Type | Meaning |
| --- | --- |
| uvicorn startup | API process started and is listening. |
| request log | Method/path/status/duration for API requests when `LOG_REQUESTS=true`. |
| slow request warning | Request duration exceeded `SLOW_REQUEST_MS`. Often expected for first AI/model-heavy requests. |
| service timing log | Embedding, relation rebuild, or explanation generation timing. |
| traceback | Error stack trace; investigate if it affects startup or important requests. |

Quick checks:

```bash
tail -n 100 runtime/noteconnect.log
grep -i "traceback\\|error\\|warning" runtime/noteconnect.log
```

## Running Tests

Compile check:

```bash
cd backend
.venv/bin/python -m compileall src main.py scripts tests
```

Unit tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

Readiness:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
```

More detail: [Test Detail](test-detail.md).

## Common Operational Checks

Check service:

```bash
curl "$API/health"
curl "$API/ready"
```

Check auth:

```bash
curl -i "$API/folders"
curl -i "$API/folders" -H "X-API-Key: wrong-key"
```

Check memory:

```bash
free -h
ps -p "$(cat runtime/noteconnect.pid)" -o pid,%mem,rss,vsz,cmd
```

Check active process:

```bash
cat runtime/noteconnect.pid
ps -p "$(cat runtime/noteconnect.pid)"
```
