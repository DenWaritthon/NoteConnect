# Phase 2: FastAPI Integration

Status: API layer implemented with singleton AI model startup and
endpoint-specific response schemas.

Phase 2 exposes the Phase 1 service layer through FastAPI while keeping SQL in
repositories and AI/business workflow in services.

## Implemented Structure

```text
backend/main.py

backend/src/api/
  dependencies.py
  schemas.py
  routers/
    health_router.py
    folder_router.py
    note_router.py
    relation_router.py
```

## Implemented Features

- FastAPI app entry point in `backend/main.py`.
- API key authentication through `X-API-Key` or the configured header name.
- Pydantic request and response schemas.
- Public health endpoint.
- Protected folder, note, and relation endpoints.
- Dedicated relation router using `/folders/{folder_id}/relations`.
- Endpoint-specific response schemas for frontend-friendly payloads.
- Partial folder update using `PATCH /folders/{folder_id}`.
- Single note detail endpoint.
- Folder `updated_at` refresh on note create/update/delete and folder metadata update.
- Folder open updates only `last_open_at`.
- FastAPI lifespan preloads shared AI services once at startup.

## Endpoints

```text
GET    /health
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

## Verification

Completed checks:

```bash
cd backend
.venv/bin/python -m compileall src scripts main.py
```

Smoke-tested:

```text
GET /health  -> 200 {"status": "ok"}
GET /folders -> 401 without X-API-Key
```

The same health and API-key guard checks were also verified through Uvicorn on
`http://127.0.0.1:8000`.

## Progress

```text
Phase 2 API Structure:              90%
Phase 2 API Authentication:         90%
Phase 2 Folder API:                 90%
Phase 2 Note API:                   90%
Phase 2 Relation API:               85%
Phase 2 Response Schemas:           90%
Phase 2 Model Startup Lifecycle:    85%
Phase 2 Documentation:              85%
```

Overall Phase 2 progress:

```text
88%
```
