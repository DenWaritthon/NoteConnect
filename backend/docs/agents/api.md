# API Rules

This file defines how Codex should design and implement API code for the NoteConnect backend.

The backend API uses FastAPI.

The API must expose backend functionality through resource-based routers while keeping business logic inside the Service layer.

---

## API Access

The backend API must use:

- FastAPI
- Pydantic schemas
- resource-based routers
- FastAPI dependencies for shared validation
- API key authentication through request headers

Rules:

- Use FastAPI routers for API endpoints.
- Use one router per main resource.
- Use Pydantic schemas for request and response validation.
- Keep route handlers thin and simple.
- Do not put business logic in API routes.
- Do not access the database directly from API routes.
- Do not call AI models directly from API routes.

---

## API Security

Protected endpoints must require an API secret key.

The API key must be provided using this request header:

```text
X-API-Key: <secret>
```

Rules:

- Read the API secret key from `.env` through a central config module.
- Read the API key header name from `.env` through a central config module.
- Do not hardcode API keys.
- Do not read `.env` directly inside route handlers.
- Validate the API key using a reusable FastAPI dependency.
- Reject requests that are missing an API key.
- Reject requests with an invalid API key.
- Do not expose the API secret key in responses, logs, or error messages.
- Do not send API keys through query strings such as `?api_key=...` because query strings are easier to leak through logs.

---

## Configuration

API-related configuration is stored in the `.env` file.

Required variables:

```text
API_SECRET_KEY=your-local-secret-key
API_KEY_HEADER_NAME=X-API-Key
```

Rules:

- Do not hardcode API configuration.
- Read configuration from environment variables.
- Use a central config module to access environment variables.
- Do not commit real API secret keys.

## API Structure

API code should be organized under `backend/src/api/`.

Example structure:

```text
backend/src/api/
  __init__.py
  dependencies.py
  schemas.py
    routers/
      __init__.py
      health_router.py
      folder_router.py
      note_router.py
      relation_router.py
```

Rules:

- Use one router file per main resource.
- Keep endpoint names clear and resource-oriented.
- Keep route handlers focused on request parsing and response formatting.
- Delegate business workflow to the Service layer.
- Use dependency injection for API key validation.
- Do not create extra router files unless the feature requires them.

---

## Pydantic Schema Rules

Use Pydantic schemas for:

- request bodies
- response bodies
- query parameters when validation is needed

Rules:

- Do not return raw database rows.
- Do not return raw DB cursors.
- Do not expose raw embeddings.
- Keep response data frontend-friendly.
- Keep schema names clear and resource-specific.

Examples:

```text
FolderCreateRequest
FolderResponse
NoteCreateRequest
NoteResponse
RelationResponse
```

---

## FastAPI Entry Point

Use `backend/main.py` as the FastAPI entry point.

Expected pattern:

```python
from fastapi import FastAPI

from src.api.routers import folder_router, health_router, note_router, relation_router

app = FastAPI(title="NoteConnect API")

app.include_router(health_router.router)
app.include_router(folder_router.router)
app.include_router(note_router.router)
app.include_router(relation_router.router)
```

Rules:

- Keep app creation simple.
- Register routers in `main.py`.
- Do not put route implementation directly in `main.py`.

---

## Folder API

The Folder API manages folders that group notes.

Responsibilities:

- create folders
- list folders
- get folder details
- open or mark a folder as active
- soft delete folders

Rules:

- Folder-specific data must use `folder_id`.
- Do not mix data across folders.
- Delete operations should be soft delete unless explicitly requested otherwise.
- Deleting a folder must follow existing database and service rules.
- Protected folder endpoints must require API key validation.

---

## Note API

The Note API manages notes inside folders.

Responsibilities:

- create notes in a folder
- list notes in a folder
- update notes
- soft delete notes
- trigger AI processing when a note is created or updated
- delete or rebuild related relations when a note is updated or deleted

Rules:

- Creating a note must trigger the note processing pipeline.
- Updating a note must trigger relation rebuild logic.
- Deleting a note must soft delete the note and clean up related relations according to Service layer rules.
- API responses must not include raw embeddings.
- API routes must delegate note workflow to the Service layer.
- Protected note endpoints must require API key validation.

---

## Relation API

Relation endpoints are exposed through a dedicated Relation API router.

Responsibilities:

- get all relations inside a folder
- return relation data already prepared in the database
- get detailed evidence data for a selected relation

Evidence for a selected relation return :
    relation_type
    similarity_score
    nli_label
    words_overlap
    similar_words

Rules:

- Use relation and evidence fields from the existing database schema.
- Do not expose unrelated internal database fields unless needed by the frontend.
- Do not recompute similarity or NLI inside relation read endpoints.
- Do not expose raw embeddings.
- Do not call AI models inside explanation read endpoints.
- Keep relation endpoints in `relation_router.py`.

---

## Health API

The Health API checks whether the backend is running.

Endpoint:

```text
GET /health
```

Responsibilities:

- return basic service status
- support development checks
- support deployment checks

Rules:

- Health endpoint may be public unless explicitly configured otherwise.
- Do not run expensive checks in the basic health endpoint.

## Error Handling

API errors should be consistent and safe.

Use clear status codes:

```text
400 Bad Request
401 Unauthorized
404 Not Found
500 Internal Server Error
```

Rules:

- Return clear error messages.
- Map service errors such as "Folder not found" or "Note not found" to HTTP 404.
- Do not expose secrets.
- Do not expose raw internal model errors.
- Do not expose database connection details.
- Log internal errors separately when logging is available.

---

## Documentation Notes

FastAPI `/docs` may still expose endpoint documentation.

Rules:

- Keep `/docs` enabled for local development unless explicitly requested otherwise.
- If production hardening is requested later, disable or protect `/docs` in production configuration.

---

## Final Constraint

Codex must focus only on API design and implementation.

API code must use FastAPI, Pydantic schemas, router separation, and reusable API key validation through the configured header.

API routes must coordinate with the Service layer and must not directly perform database or AI model operations.
