# Phase 2: FastAPI Integration

Status: Complete and verified through API contract tests plus real database
integration testing.

## Goal

Expose the Phase 1 production service layer through a standard FastAPI API while
keeping business logic in services and SQL in repositories.

## What Was Built

- Added FastAPI app entry point in `backend/main.py`.
- Added app factory and lifespan startup wiring.
- Added API key authentication through `X-API-Key` or configured header name.
- Added Pydantic request and response schemas.
- Added health/readiness API structure.
- Added folder endpoints for create, list, detail, update, open, and soft delete.
- Added note endpoints for create, list, detail, update, and soft delete.
- Added relation endpoints for listing relations and reading evidence.
- Split API routers by resource: folder, note, relation, health.
- Added partial folder update support.
- Added single note detail endpoint.
- Added folder timestamp rules:
  - folder open updates only `last_open_at`
  - note/folder metadata changes update `updated_at`
- Added startup model/service reuse so note writes do not reload AI models per
  request.

## Result

Phase 2 turned the core backend into an API service that can be called by curl,
frontend clients, or internal tools.

The API now supports:

- protected folder workflows
- protected note workflows
- relation and evidence reads
- frontend-friendly response contracts
- API-key-based access control
- stable resource-based endpoint structure

## API Surface Added

```text
GET    /health
GET    /ready
POST   /folders
GET    /folders
GET    /folders/{folder_id}
PATCH  /folders/{folder_id}
PATCH  /folders/{folder_id}/open
DELETE /folders/{folder_id}
POST   /folders/{folder_id}/notes
GET    /folders/{folder_id}/notes
GET    /folders/{folder_id}/notes/{note_id}
PUT    /folders/{folder_id}/notes/{note_id}
DELETE /folders/{folder_id}/notes/{note_id}
GET    /folders/{folder_id}/relations
GET    /folders/{folder_id}/relations/{relation_id}/evidence
```

## Verification Outcome

Verification passed with:

- compile checks
- API contract tests
- API key rejection checks
- response schema checks
- real database/API workflow testing during development

The tested API paths passed and matched the intended response contracts.

## Progress

```text
Overall Phase 2 progress: 100%
```
