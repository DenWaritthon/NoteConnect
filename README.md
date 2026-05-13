# NoteConnect Backend

NoteConnect Backend is a FastAPI service for AI-assisted note relationship
discovery. It stores notes in PostgreSQL, creates sentence embeddings, searches
similar notes with pgvector, classifies relationships with NLI, stores relation
evidence, and can generate one-time explanations for each relation.

## Tech Stack

| Area | Technology |
| --- | --- |
| API | FastAPI, Pydantic |
| Runtime | Python 3.12, Uvicorn |
| Database | PostgreSQL, pgvector |
| DB Driver | psycopg3 |
| Embedding | local clone of `sentence-transformers/all-mpnet-base-v2` |
| NLI | local clone of `cross-encoder/nli-deberta-v3-base` |
| Explanation | local clone of `Qwen/Qwen3-0.6B` |
| Deployment Target | Internal Ubuntu server with `nohup` |

## What This Backend Does

- Manages folders and notes through an API protected by `X-API-Key`.
- Converts each note sentence into an embedding.
- Finds similar notes inside the same folder with PostgreSQL pgvector.
- Uses NLI to classify whether two notes are related, entailment-like, or conflicting.
- Stores relation evidence such as similarity score, NLI label, word overlap,
  similar words, and `llm_payload`.
- Generates relation explanations from stored `llm_payload` only.
- Uses soft delete for folders, notes, relations, and evidence.
- Supports internal Ubuntu deployment with `nohup`, local model files, and
  offline model readiness checks.

## Current Completion

The backend is complete for the current internal/nohup deployment target. It
supports folder/note CRUD, relation discovery, evidence storage, explanation
generation, API access, server readiness checks, logging, and production-safe
unit tests.

For phase-by-phase status, see
[Backend Progress Status](backend/docs/progrest/progrest-status.md).

## How It Works

```text
Client / curl / frontend
        |
        v
FastAPI API layer
        |
        v
Service layer
        |
        v
Data repository layer
        |
        v
PostgreSQL + pgvector
```

Database overview:

- `noteconnect_folder` stores folders and folder timestamps.
- `noteconnect_note` stores note sentences and `vector(768)` embeddings.
- `noteconnect_note_relation` stores confirmed note pairs and process status.
- `noteconnect_note_relation_evidence` stores similarity/NLI evidence,
  `llm_payload`, and optional generated explanation.
- PostgreSQL extensions `pgcrypto` and `vector` support UUID defaults and
  pgvector similarity search.
- Baseline indexes support active-record reads, relation lookups, latest
  evidence lookup, and HNSW vector search.

More detail: [Database Detail](backend/docs/system-manual/database-detail.md).

Typical note flow:

1. Client creates or updates a note.
2. `NoteService` validates the folder and sentence.
3. `SentenceProcessor` creates the embedding.
4. PostgreSQL pgvector searches similar notes in the same folder.
5. NLI and relation rules decide whether to store a relation.
6. Relation evidence and `llm_payload` are saved to the database.
7. Folder `updated_at` is refreshed.

Explanation flow:

1. Client calls `POST /folders/{folder_id}/relations/{relation_id}/explanation`.
2. `ExplanationService` loads the latest active evidence.
3. The generator uses only `note_relation_evidence.llm_payload`.
4. The explanation is stored once and reused on later calls.

## Main Files

```text
backend/main.py             FastAPI entry point
backend/src/api/            Routers, schemas, API dependencies
backend/src/services/       Business workflows and AI pipeline coordination
backend/src/data/           psycopg3 repositories and SQL access
backend/src/core/           Config, database helpers, logging
backend/database/           Manual database SQL reference and setup files
backend/model/              Local AI model directories prepared with Git LFS
backend/scripts/            Server checks and nohup runner scripts
backend/tests/              Fast production-safe unit tests
backend/docs/system-manual/ Detailed backend manual
```

More detail: [File Structure](backend/docs/system-manual/file-structure.md).

## Quick Start

Create `backend/.env` from `backend/.env.example`, then configure database,
API key, model, and runtime values.

Run locally:

```bash
cd backend
bash scripts/run_server.sh
```

Configured local/server URL:

```text
http://127.0.0.1:6550
```

Health check:

```bash
curl "http://127.0.0.1:6550/health"
```

Protected request example:

```bash
curl "http://127.0.0.1:6550/folders" \
  -H "X-API-Key: your-secret"
```

Run tests:

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

More detail:

- [Usage Guide](backend/docs/system-manual/usage-guide.md)
- [Server Deploy Guide](backend/docs/system-manual/server-deploy.md)
- [Test Detail](backend/docs/system-manual/test-detail.md)
- [Backend Progress Status](backend/docs/progrest/progrest-status.md)

## API Summary

Protected endpoints require `X-API-Key: <secret>`. `GET /health` and
`GET /ready` are public.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check that the API process is running. |
| `GET` | `/ready` | Check runtime, database, and model readiness. |
| `POST` | `/folders` | Create a folder. |
| `GET` | `/folders` | List active folders. |
| `GET` | `/folders/{folder_id}` | Get one active folder. |
| `PATCH` | `/folders/{folder_id}` | Update folder name and/or description. |
| `PATCH` | `/folders/{folder_id}/open` | Update only `last_open_at`. |
| `DELETE` | `/folders/{folder_id}` | Soft delete a folder and its child records. |
| `POST` | `/folders/{folder_id}/notes` | Create a note and run the relation pipeline. |
| `GET` | `/folders/{folder_id}/notes` | List active notes in a folder. |
| `GET` | `/folders/{folder_id}/notes/{note_id}` | Get one active note. |
| `PUT` | `/folders/{folder_id}/notes/{note_id}` | Update a note and rebuild its relations. |
| `DELETE` | `/folders/{folder_id}/notes/{note_id}` | Soft delete a note and connected relations/evidence. |
| `GET` | `/folders/{folder_id}/relations` | List active relations in a folder. |
| `GET` | `/folders/{folder_id}/relations/{relation_id}/evidence` | Get latest active evidence for a relation. |
| `GET` | `/folders/{folder_id}/relations/{relation_id}/explanation` | Read an existing explanation only. |
| `POST` | `/folders/{folder_id}/relations/{relation_id}/explanation` | Generate explanation once, or return the existing explanation. |

Full request/response examples: [API Reference](backend/docs/system-manual/api-reference.md).

## Backend Limitations

- The current deployment target is internal/private API usage with `nohup`, not
  public internet exposure.
- No sudo-managed systemd service is included yet.
- No nginx/TLS configuration is included for the current target.
- Database schema and index SQL are applied manually outside the application.
- Local model files must be prepared before startup; Git LFS pointer files are
  not usable model weights.
- Heavy load testing and advanced monitoring are future hardening work.
- AI model memory usage depends on server resources; `EXPLANATION_LOAD_MODE=lazy`
  is recommended on small servers.
- Explanation generation has no regenerate/replace endpoint by design.
- The POC in `backend/poc/` is reference-only and should not be modified unless
  explicitly requested.

## Documentation

- [System Architecture](backend/docs/system-manual/system-architecture.md)
- [File Structure](backend/docs/system-manual/file-structure.md)
- [Database Detail](backend/docs/system-manual/database-detail.md)
- [API Reference](backend/docs/system-manual/api-reference.md)
- [Usage Guide](backend/docs/system-manual/usage-guide.md)
- [Server Deploy Guide](backend/docs/system-manual/server-deploy.md)
- [Test Detail](backend/docs/system-manual/test-detail.md)
