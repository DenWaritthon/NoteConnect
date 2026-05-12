# Backend System Architecture

This document describes how the NoteConnect backend works at a system level.

## Overview

NoteConnect is an AI note relationship backend. It stores notes inside folders,
generates sentence embeddings, searches for similar notes with pgvector,
classifies note relationships with NLI, and stores relation evidence in
PostgreSQL. It can also generate relation explanations from stored evidence
payloads.

The backend has two main usage paths:

- Terminal demo for Phase 1 manual testing.
- FastAPI service for Phase 2 API access.
- Automated tests for API contracts, service workflow, and real Phase 1-3
  database/model integration.

## Layered Architecture

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

## API Layer

Location:

```text
backend/src/api/
```

Responsibilities:

- Receive HTTP requests.
- Validate API key headers.
- Validate request and response schemas with Pydantic.
- Convert service errors into safe HTTP errors.
- Return frontend-friendly responses.

Rules:

- API routes do not run SQL.
- API routes do not call AI models directly.
- API routes delegate workflow to services.
- API responses do not expose raw embeddings.

## Service Layer

Location:

```text
backend/src/services/
```

Responsibilities:

- Validate user-facing inputs.
- Coordinate transactions.
- Run the note relation workflow.
- Generate embeddings and NLI predictions through `SentenceProcessor`.
- Trigger relation rebuild when notes change.
- Apply soft delete rules.

Main services:

- `FolderService`: folder create, update, open, list, and soft delete.
- `NoteService`: note create, update, delete, list, detail, and relation rebuild.
- `RelationService`: relation classification rules.
- `RelationQueryService`: relation and evidence read workflows for the API.
- `ExplanationService`: relation explanation read/create workflow.
- `ExplanationGenerator`: LLM-backed explanation text generation.
- `SentenceProcessor`: embedding, NLI, word overlap, and similar word logic.

## Data Layer

Location:

```text
backend/src/data/
```

Responsibilities:

- Own all SQL statements.
- Map database rows into typed dataclasses.
- Run pgvector similarity queries in PostgreSQL.
- Persist notes, relations, and evidence.

Repositories:

- `FolderRepository`
- `NoteRepository`
- `RelationRepository`
- `EvidenceRepository`

## Core Layer

Location:

```text
backend/src/core/
```

Responsibilities:

- Load configuration from `.env`.
- Build database connection settings.
- Provide transaction helpers.
- Register pgvector support for psycopg.

## Note Creation Workflow

```text
POST /folders/{folder_id}/notes
        |
        v
NoteService.create_note()
        |
        v
Validate folder and sentence
        |
        v
Generate embedding
        |
        v
Insert note
        |
        v
Find similar notes with pgvector
        |
        v
Run NLI and relation classification
        |
        v
Store note_relation and note_relation_evidence
        |
        v
Touch folder.updated_at
```

## Note Update Workflow

Updating a note rebuilds its active relations:

```text
PUT /folders/{folder_id}/notes/{note_id}
        |
        v
Soft delete active relations for that note
        |
        v
Update sentence and embedding
        |
        v
Rebuild relations against similar notes
        |
        v
Touch folder.updated_at
```

## Folder Timestamp Rules

- `created_at`: set when the folder is created.
- `last_open_at`: updated only when `PATCH /folders/{folder_id}/open` is called.
- `updated_at`: updated when folder metadata changes or notes are created,
  updated, or deleted.

Opening a folder does not update `updated_at`.

## AI Model Lifecycle

FastAPI uses lifespan startup to create long-lived services once:

```text
backend/main.py
```

The shared `SentenceProcessor` is created during startup and reused by
`NoteService`, so note create/update requests do not reload AI models per
request. The shared `ExplanationGenerator` is also created during startup and
reused by `ExplanationService`.

## Explanation Workflow

```text
POST /folders/{folder_id}/relations/{relation_id}/explanation
        |
        v
ExplanationService.create_explanation()
        |
        v
Load latest active evidence and llm_payload
        |
        v
Generate explanation from llm_payload
        |
        v
Store explanation on note_relation_evidence
        |
        v
Set relation process_status to add_explanation
```

`GET /folders/{folder_id}/relations/{relation_id}/explanation` is read-only. It
returns an existing explanation or `404` when no explanation exists.

## Test Architecture

The backend uses two test layers:

- Fast tests in `backend/tests/` use `unittest`, FastAPI `TestClient`, fake
  services, and fake repositories to verify API contracts and service behavior
  without loading models or connecting to PostgreSQL.
- Server readiness scripts in `backend/scripts/` verify deploy config, imports,
  package availability, and database connectivity without writing application
  data or loading AI models.

Development real integration testing can still be run from a full development
checkout when the manual script is available. That script is intentionally not
part of the minimal production server deploy script set.

See [Test Detail](test-detail.md) for commands, coverage, and the latest test
result.

## Soft Delete Rules

The backend uses soft delete behavior for user data:

- Folder delete marks the folder, child notes, child relations, and evidence as deleted.
- Note delete marks the note and connected relations/evidence as deleted.
- Read endpoints return active records only.
