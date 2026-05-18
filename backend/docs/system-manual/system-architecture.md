# Backend System Architecture

This document explains how the NoteConnect backend is structured and how each
supported workflow moves through the system.

## System Purpose

NoteConnect is an AI note relationship backend. It receives notes through a
FastAPI API, stores them in PostgreSQL, searches similar notes with pgvector,
classifies relationships with NLI, stores evidence, and generates explanations
from saved `llm_payload` when requested.

The current deployment target is an internal/private API running on Ubuntu with
`nohup`.

## High-Level Architecture

```text
Client / curl / frontend
        |
        v
FastAPI routers
        |
        v
Service layer
        |
        v
Repository layer
        |
        v
PostgreSQL + pgvector
```

Layer responsibilities:

| Layer | Location | Responsibility |
| --- | --- | --- |
| API | `backend/src/api/` | Request parsing, API key validation, Pydantic response contracts. |
| Service | `backend/src/services/` | Business workflow, AI coordination, transactions, soft delete rules. |
| Data | `backend/src/data/` | psycopg3 SQL execution and row mapping. |
| Core | `backend/src/core/` | Config, DB connection helpers, logging, shared constants. |
| Database | `backend/database/` | Manual SQL setup/reference files. |

API routes do not run SQL or call AI models directly. Services do not contain
SQL. Repositories are the only production layer that owns SQL statements.

## Startup Lifecycle

```text
uvicorn main:app
        |
        v
create_app()
        |
        v
load .env config
        |
        v
install request logging
        |
        v
lifespan startup
        |
        v
create shared repositories and services
        |
        v
API ready
```

`SentenceProcessor` is shared by the application so note create/update does not
reload embedding and NLI models per request. Explanation generation supports
`EXPLANATION_LOAD_MODE=lazy`, which loads the explanation model only during
`POST /explanation` and releases it afterward. Model references are resolved to
local paths when configured with `./model/...`, and loaders use local files only
so the backend does not depend on internet access at runtime.

## Folder Workflows

### Create Folder

```text
POST /folders
        |
        v
FolderService.create_folder()
        |
        v
FolderRepository.insert
        |
        v
return folder_id, name, created_at
```

### Update Folder

```text
PATCH /folders/{folder_id}
        |
        v
validate name and/or description
        |
        v
update folder metadata
        |
        v
touch updated_at
```

`PATCH /folders/{folder_id}` accepts partial updates. Sending only `name` or
only `description` is valid.

### Open Folder

```text
PATCH /folders/{folder_id}/open
        |
        v
update last_open_at only
```

Opening a folder does not update `updated_at`.

### Delete Folder

```text
DELETE /folders/{folder_id}
        |
        v
soft delete folder
        |
        v
soft delete child notes, relations, and evidence
```

Read endpoints return active records only.

## Note Create Pipeline

```text
POST /folders/{folder_id}/notes
        |
        v
NoteService.create_note()
        |
        v
validate folder and sentence
        |
        v
generate sentence embedding
        |
        v
insert note with embedding
        |
        v
search similar notes in same folder using pgvector
        |
        v
run NLI and relation rules
        |
        v
store note_relation
        |
        v
store note_relation_evidence with llm_payload
        |
        v
touch folder.updated_at
```

Similarity search stays inside PostgreSQL. The backend does not compare
embeddings manually in Python for production logic.

## Note Update Pipeline

```text
PUT /folders/{folder_id}/notes/{note_id}
        |
        v
validate active note
        |
        v
soft delete existing active relations/evidence for that note
        |
        v
generate new embedding
        |
        v
update note sentence and embedding
        |
        v
rebuild relations against similar active notes
        |
        v
touch folder.updated_at
```

Updating a note does not attempt to preserve or regenerate previous relation
explanations. New relations receive new evidence.

## Note Delete Pipeline

```text
DELETE /folders/{folder_id}/notes/{note_id}
        |
        v
soft delete note
        |
        v
soft delete connected relations and evidence
        |
        v
touch folder.updated_at
```

## Relation Read Pipeline

```text
GET /folders/{folder_id}/relations
        |
        v
RelationQueryService.list_relations()
        |
        v
return relation_id and note sentence pairs
```

```text
GET /folders/{folder_id}/relations/{relation_id}/evidence
        |
        v
load latest active evidence
        |
        v
return relation_type, similarity_score, nli_label, overlap, similar_words
```

Relation read endpoints do not recompute similarity, NLI, or explanations.

## Explanation Pipeline

```text
GET /folders/{folder_id}/relations/{relation_id}/explanation
        |
        v
load latest active evidence
        |
        v
return existing explanation or 404
```

`GET` is read-only. It never generates text and never writes to the database.

```text
POST /folders/{folder_id}/relations/{relation_id}/explanation
        |
        v
load latest active evidence
        |
        v
if explanation exists, return it
        |
        v
validate llm_payload
        |
        v
generate explanation
        |
        v
save explanation to note_relation_evidence
        |
        v
set note_relation.process_status = add_explanation
```

There is no regenerate, replace, or `PUT` explanation endpoint. Explanation
input must come from `note_relation_evidence.llm_payload`.

## Timestamp Rules

| Event | `created_at` | `updated_at` | `last_open_at` |
| --- | --- | --- | --- |
| Create folder | set | set | may be null/initial |
| Open folder | unchanged | unchanged | updated |
| Update folder metadata | unchanged | updated | unchanged |
| Create note | unchanged on folder | folder updated | unchanged |
| Update note | unchanged on folder | folder updated | unchanged |
| Delete note | unchanged on folder | folder updated | unchanged |

## Process Status

`note_relation.process_status` currently uses:

| Status | Meaning |
| --- | --- |
| `relation_confirmed` | Relation and evidence were saved. |
| `add_explanation` | Explanation was added to latest active evidence. |

## Soft Delete Model

Deletes are soft deletes. The system marks `deleted_at` and filters active
records in read paths. This applies to folders, notes, relations, and evidence.

## Logging And Readiness

Request logging is controlled by:

```env
LOG_REQUESTS=true
SLOW_REQUEST_MS=3000
```

Readiness is exposed through:

```text
GET /health
GET /ready
```

`/health` checks that the process is alive. `/ready` can check database
connectivity when `READY_CHECK_DATABASE=true` and also checks model readiness:

```text
GET /ready
        |
        v
optional DB connectivity check
        |
        v
embedding/NLI loaded status from NoteService
        |
        v
explanation model verified loadable
        |
        v
ready response or 503
```

With `EXPLANATION_LOAD_MODE=lazy`, the explanation model is loaded once for
verification and then unloaded. This keeps `/ready` meaningful without turning
lazy mode into permanent RAM usage.
