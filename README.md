# NoteConnect Backend

NoteConnect backend is a system for AI-assisted note relationship discovery.
It stores notes in folders, generates sentence embeddings, searches similar
notes with PostgreSQL pgvector, classifies relationships with NLI, and exposes
the workflow through a FastAPI API.

## Current Status

```text
Phase 1 Core Production Pipeline: 100%
Phase 2 FastAPI Integration:      100%
Phase 3 Explanation Pipeline:     100%
Phase 4 Internal/nohup Deploy:    100%
Phase 5 Internal Optimization:    100%
```

Progress details:

- [Phase 1 Progress](backend/docs/progrest/phase-1.md)
- [Phase 2 Progress](backend/docs/progrest/phase-2.md)
- [Phase 3 Progress](backend/docs/progrest/phase-3.md)
- [Phase 4 Progress](backend/docs/progrest/phase-4.md)
- [Phase 5 Progress](backend/docs/progrest/phase-5.md)

## Backend Overview

The backend is organized into clear layers:

```text
FastAPI API layer
Service layer
Data repository layer
PostgreSQL + pgvector
```

Core behavior:

- Folders group notes.
- Notes store text and embeddings.
- Similarity search runs in PostgreSQL using pgvector.
- NLI validates whether similar notes are entailment, semantic, or conflict relations.
- Relation evidence stores similarity score, NLI label, word overlap, and similar words.
- Relation explanations can be generated from stored `llm_payload`.
- Deletions use soft delete behavior.
- API access is protected by an API key header.

Detailed manuals:

- [System Architecture](backend/docs/system-manual/system-architecture.md)
- [File Structure](backend/docs/system-manual/file-structure.md)
- [API Reference](backend/docs/system-manual/api-reference.md)
- [Usage Guide](backend/docs/system-manual/usage-guide.md)
- [Server Deploy Guide](backend/docs/system-manual/server-deploy.md)
- [Test Detail](backend/docs/system-manual/test-detail.md)

## Quick Start

Create `backend/.env` using `backend/.env.example` as the reference.

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
```

Run the API:

```bash
cd backend
bash scripts/run_server.sh
```

Check that the API is running:

```bash
curl "http://127.0.0.1:8000/health"
```

Expected response:

```json
{
  "status": "ok"
}
```

Call a protected endpoint:

```bash
curl "http://127.0.0.1:8000/folders" \
  -H "X-API-Key: your-secret"
```

Open the local API docs:

```text
http://127.0.0.1:8000/docs
```

Run automated tests:

```bash
cd backend
.venv/bin/python -m unittest discover -s tests
```

Run deploy readiness checks:

```bash
cd backend
.venv/bin/python scripts/check_deploy_ready.py
.venv/bin/python scripts/check_db_ready.py
```

Latest verified test result:

```text
Deploy readiness checks: PASS
DB readiness check: PASS
Fast tests: 25 passed
Phase 5 server deploy verification: PASS
Real integration checks: 22 passed
```

Server readiness checks verify config, imports, packages, and DB connectivity
without writing application data or loading AI models. More detail is in the
[Test Detail](backend/docs/system-manual/test-detail.md).

For the internal Ubuntu server deployment flow using `nohup`, see the
[Server Deploy Guide](backend/docs/system-manual/server-deploy.md).

Apply database performance indexes after the schema exists:

```bash
cd backend
psql "$DATABASE_URL" -f database/create_index.sql
```

## Common API Flow

1. Create a folder with `POST /folders`.
2. Add notes with `POST /folders/{folder_id}/notes`.
3. List notes with `GET /folders/{folder_id}/notes`.
4. List relations with `GET /folders/{folder_id}/relations`.
5. Inspect evidence with `GET /folders/{folder_id}/relations/{relation_id}/evidence`.
6. Create or read explanation with `POST` or `GET /folders/{folder_id}/relations/{relation_id}/explanation`.

For full request and response examples, see the
[API Reference](backend/docs/system-manual/api-reference.md).

## Development Notes

- Production code lives in `backend/src/`.
- FastAPI entry point is `backend/main.py`.
- Database SQL files live in `backend/database/`.
- The POC in `backend/poc/` is kept as a reference and should not be modified unless explicitly requested.
- Do not commit real `.env` secrets.
