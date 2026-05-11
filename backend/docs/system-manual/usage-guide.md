# Backend Usage Guide

This guide explains how to run and use the NoteConnect backend locally.

## Prerequisites

- Python virtual environment in `backend/.venv`.
- PostgreSQL database with pgvector enabled.
- Database schema applied from `backend/database/`.
- `backend/.env` configured.

## Environment Configuration

Use `backend/.env.example` as the reference.

Important variables:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=noteconnect
DB_USER=postgres
DB_PASSWORD=your-password

API_SECRET_KEY=your-secret
API_KEY_HEADER_NAME=X-API-Key

EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
NLI_MODEL=cross-encoder/nli-deberta-v3-base
EXPLANATION_MODEL=Qwen/Qwen3-0.6B
EXPLANATION_MAX_NEW_TOKENS=128
EMBEDDING_DIMENSION=768

SIMILARITY_THRESHOLD=0.40
THRESHOLD_SCALE=0.20
SIMILARITY_TOP_K=10
SIMILAR_WORD_THRESHOLD=0.55
```

Do not commit real `.env` secrets.

## Run The API

```bash
cd backend
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```bash
curl "http://127.0.0.1:8000/health"
```

Expected response:

```json
{
  "status": "ok"
}
```

## API Key Check

Protected endpoints require the API key header.

Without the key:

```bash
curl -i "http://127.0.0.1:8000/folders"
```

Expected status:

```text
401 Unauthorized
```

With the key:

```bash
curl "http://127.0.0.1:8000/folders" \
  -H "X-API-Key: your-secret"
```

## Create A Folder

```bash
curl -X POST "http://127.0.0.1:8000/folders" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Study Notes\",\"description\":\"Learning notes\"}"
```

Copy the returned `folder_id` for later requests.

## Update A Folder

Update only the name:

```bash
curl -X PATCH "http://127.0.0.1:8000/folders/<folder_id>" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated Study Notes\"}"
```

Update only the description:

```bash
curl -X PATCH "http://127.0.0.1:8000/folders/<folder_id>" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"description\":\"I'm updating only the description.\"}"
```

Clear the description:

```bash
curl -X PATCH "http://127.0.0.1:8000/folders/<folder_id>" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"description\":null}"
```

## Open A Folder

```bash
curl -X PATCH "http://127.0.0.1:8000/folders/<folder_id>/open" \
  -H "X-API-Key: your-secret"
```

This updates only `last_open_at`.

## Create Notes

```bash
curl -X POST "http://127.0.0.1:8000/folders/<folder_id>/notes" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pizza.\"}"
```

Add a second related note:

```bash
curl -X POST "http://127.0.0.1:8000/folders/<folder_id>/notes" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I am studying pizza cooking.\"}"
```

Note creation may take time on the first run because the API loads AI models at
server startup. After startup, note writes reuse the shared model service.

## List Notes

```bash
curl "http://127.0.0.1:8000/folders/<folder_id>/notes" \
  -H "X-API-Key: your-secret"
```

## Get One Note

```bash
curl "http://127.0.0.1:8000/folders/<folder_id>/notes/<note_id>" \
  -H "X-API-Key: your-secret"
```

## Update A Note

```bash
curl -X PUT "http://127.0.0.1:8000/folders/<folder_id>/notes/<note_id>" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pasta.\"}"
```

Updating a note rebuilds active relations connected to that note.

## Delete A Note

```bash
curl -X DELETE "http://127.0.0.1:8000/folders/<folder_id>/notes/<note_id>" \
  -H "X-API-Key: your-secret"
```

This soft deletes the note and its connected relations/evidence.

## List Relations

```bash
curl "http://127.0.0.1:8000/folders/<folder_id>/relations" \
  -H "X-API-Key: your-secret"
```

Copy the returned `relation_id` to inspect evidence.

## Get Relation Evidence

```bash
curl "http://127.0.0.1:8000/folders/<folder_id>/relations/<relation_id>/evidence" \
  -H "X-API-Key: your-secret"
```

## Get Relation Explanation

```bash
curl "http://127.0.0.1:8000/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: your-secret"
```

If no explanation exists yet, this returns `404 Explanation not found.` because
`GET` is read-only.

## Create Relation Explanation

```bash
curl -X POST "http://127.0.0.1:8000/folders/<folder_id>/relations/<relation_id>/explanation" \
  -H "X-API-Key: your-secret"
```

If an explanation already exists, this returns the existing explanation. It does
not regenerate or replace explanation text.

## Delete A Folder

```bash
curl -X DELETE "http://127.0.0.1:8000/folders/<folder_id>" \
  -H "X-API-Key: your-secret"
```

This soft deletes the folder, notes, relations, and relation evidence.

## Curl Quoting Notes

When JSON text contains an apostrophe, such as `I'm`, do not wrap the whole JSON
payload in single quotes. This causes the shell to wait for more input and show
`dquote>`.

Use escaped double quotes:

```bash
curl -X POST "http://127.0.0.1:8000/folders/<folder_id>/notes" \
  -H "X-API-Key: your-secret" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pizza.\"}"
```

Alternatively, place the JSON in a file and send it with `--data @file.json`.

## Run Tests

Run compile checks:

```bash
cd backend
.venv/bin/python -m compileall src main.py scripts tests
```

Run fast automated tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

Run the real Phase 1-3 database and model integration test:

```bash
cd backend
.venv/bin/python scripts/run_phase1_3_real_test.py
```

The real integration test uses the configured `.env`, loads real models, writes
temporary rows into PostgreSQL, verifies API and database behavior, and cleans
up the test folder with soft delete.

For the full test design and latest results, see
[Test Detail](test-detail.md).

## Terminal Demo

Phase 1 also provides a terminal demo:

```bash
cd backend
.venv/bin/python scripts/terminal_demo.py
```

The terminal demo writes to the real database and follows the same core service
logic as the production backend.
