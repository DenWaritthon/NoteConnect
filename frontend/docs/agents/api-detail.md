# Frontend API Integration Guide

This document describes how the frontend should communicate with the existing NoteConnect backend API server.

The backend server already exists.
The frontend must behave as a clean API client.

The frontend must:

- fetch and display backend data
- submit user actions through API requests
- handle loading, empty, success, and error states
- normalize API errors into user-friendly UI behavior
- avoid duplicating backend business logic

The frontend must not:

- access the database directly
- reimplement backend pipelines
- recompute relations client-side
- bypass API authentication rules

## API Base URL

Local development:

```text
http://127.0.0.1:6550
```

Production values must come from environment variables.

Example:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:6550
```

## Authentication

Protected endpoints require:

Development and trusted environments may call the API directly with:

```http
X-API-Key: your-secret
```

Production browser clients must not expose private API keys.

For production, use one of these approaches:
- a backend-for-frontend proxy
- server-side route handlers
- session-based auth
- another secure auth mechanism approved by the backend architecture

Only expose environment variables prefixed with `NEXT_PUBLIC_` when the value is safe to be public.

Frontend responsibilities:

- centralize authentication header handling
- avoid hardcoding secrets
- avoid exposing private API keys in browser bundles
- use secure server-side proxying when needed
- store configuration in environment variables
- handle unauthorized responses gracefully
- redirect or reset state when authentication fails

`GET /health` and `GET /ready` are public.

## Endpoint Summary

| Method | Endpoint | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Process health check. |
| `GET` | `/ready` | No | Runtime readiness and optional DB check. |
| `POST` | `/folders` | Yes | Create folder. |
| `GET` | `/folders` | Yes | List active folders. |
| `GET` | `/folders/{folder_id}` | Yes | Get one folder. |
| `PATCH` | `/folders/{folder_id}` | Yes | Update folder name and/or description. |
| `PATCH` | `/folders/{folder_id}/open` | Yes | Update only `last_open_at`. |
| `DELETE` | `/folders/{folder_id}` | Yes | Soft delete folder and child records. |
| `POST` | `/folders/{folder_id}/notes` | Yes | Create note and run relation pipeline. |
| `GET` | `/folders/{folder_id}/notes` | Yes | List active notes. |
| `GET` | `/folders/{folder_id}/notes/{note_id}` | Yes | Get one note. |
| `PUT` | `/folders/{folder_id}/notes/{note_id}` | Yes | Update note and rebuild relations. |
| `DELETE` | `/folders/{folder_id}/notes/{note_id}` | Yes | Soft delete note and connected relations/evidence. |
| `GET` | `/folders/{folder_id}/relations` | Yes | List active relations. |
| `GET` | `/folders/{folder_id}/relations/{relation_id}/evidence` | Yes | Get latest active relation evidence. |
| `GET` | `/folders/{folder_id}/relations/{relation_id}/explanation` | Yes | Read existing explanation only. |
| `POST` | `/folders/{folder_id}/relations/{relation_id}/explanation` | Yes | Generate explanation once or return existing explanation. |

## Frontend API Architecture Rules

Frontend code should not call fetch APIs directly inside large UI components.

Use a shared API layer:

```text
src/
  services/
    api/
      folders.ts
      notes.ts
      relations.ts
```

Responsibilities of the API layer:

- build request URLs
- attach headers
- parse JSON responses
- normalize API errors
- expose typed request helpers
- isolate backend contract changes

Example:

```ts
export async function getFolders(): Promise<Folder[]> {
  return apiClient.get('/folders');
}
```

Frontend pages and features should consume typed service functions instead of raw fetch calls.

## API Client Conventions

Use one shared API client for common behavior.

The client should handle:
- base URL configuration
- auth/header attachment
- JSON parsing
- non-2xx response handling
- network errors
- request cancellation when useful

Suggested shape:

```ts
type ApiClientOptions = {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
};

async function apiRequest<T>(path: string, options?: ApiClientOptions): Promise<T> {
  // Centralized request handling lives here.
}
```

## Naming and Data Mapping

The backend API uses `snake_case` response fields.

Frontend code may choose one of two strategies:

1. Preserve API response shapes in service return values.
2. Map API responses to frontend-friendly `camelCase` models inside the Service layer.

Whichever strategy is used, keep it consistent across all services.

Do not perform ad-hoc field mapping inside UI components.

## Shared Frontend Types

Define shared API/domain types in `src/types/` or the existing project convention.

Example types:

```ts
type Folder = {
  folder_id: string;
  name: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
  last_open_at?: string | null;
};

type Note = {
  note_id: string;
  folder_id: string;
  sentence: string;
  created_at?: string;
  updated_at?: string;
};

type Relation = {
  relation_id: string;
  note_1_id: string;
  note_1_sentence: string;
  note_2_id: string;
  note_2_sentence: string;
};

type RelationEvidence = {
  relation_id: string;
  relation_type: string;
  similarity_score: number;
  nli_label?: string;
  words_overlap?: string[];
  similar_words?: Array<{
    word1: string;
    word2: string;
    score: number;
  }>;
};

type RelationExplanation = {
  relation_id: string;
  explanation: string;
};
```

## Cache and Refresh Expectations

After successful mutations, refresh or invalidate affected data.

Expected behavior:
- creating a folder refreshes folder lists
- updating a folder refreshes folder detail and folder lists
- deleting a folder refreshes folder lists and clears selected-folder state if needed
- creating a note refreshes note lists and relations
- updating a note refreshes note detail, note lists, and relations
- deleting a note refreshes note lists and relations
- generating an explanation refreshes relation explanation state

Avoid showing stale relation or graph data after note changes.

## Health

### GET /health

Checks whether the API process is alive.

Response:

```json
{
  "status": "ok"
}
```

### GET /ready

Checks whether the API is ready to serve. When `READY_CHECK_DATABASE=true`, it
also verifies database connectivity.

Response:

```json
{
  "status": "ready",
  "database": "ok",
  "explanation_load_mode": "lazy"
}
```

If the database check fails, the endpoint returns `503`.

## Folders

### POST /folders

Request body:

```json
{
  "name": "Study Notes",
  "description": "Learning notes"
}
```

Response:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Study Notes",
  "created_at": "2026-05-07T10:00:00.000000"
}
```

### GET /folders

Lists active folders. Deleted folders are not returned.

Response:

```json
[
  {
    "folder_id": "11111111-1111-1111-1111-111111111111",
    "name": "Study Notes",
    "last_open_at": "2026-05-07T10:10:00.000000"
  }
]
```

### GET /folders/{folder_id}

Gets one active folder with metadata.

Response:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Study Notes",
  "description": "Learning notes",
  "created_at": "2026-05-07T10:00:00.000000",
  "updated_at": "2026-05-07T10:20:00.000000",
  "last_open_at": "2026-05-07T10:10:00.000000"
}
```

### PATCH /folders/{folder_id}

Request body:

```json
{
  "name": "Updated Study Notes",
  "description": "I'm updating the description."
}
```

Response:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Updated Study Notes",
  "description": "I'm updating the description.",
  "updated_at": "2026-05-07T10:20:00.000000"
}
```

### PATCH /folders/{folder_id}/open

Marks the folder as opened by updating only `last_open_at`. It does not update
folder `updated_at`.

Response:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "last_open_at": "2026-05-07T10:25:00.000000"
}
```

### DELETE /folders/{folder_id}

Soft deletes the folder, child notes, child relations, and child evidence.

Response:

```json
{
  "deleted": true
}
```

## Notes

### POST /folders/{folder_id}/notes

Request body:

```json
{
  "sentence": "I'm learning how to make pizza."
}
```

Creates a note and runs the relation pipeline:

```text
embedding -> pgvector similarity search -> NLI -> relation/evidence write
```

Frontend behavior expectations:

- disable duplicate submissions while saving
- show pending/loading UI
- refresh related note/relation data after success
- handle validation and API errors clearly

Response:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pizza.",
  "created_at": "2026-05-07T10:30:00.000000"
}
```

### GET /folders/{folder_id}/notes

Lists active notes in a folder.

Response:

```json
[
  {
    "note_id": "22222222-2222-2222-2222-222222222222",
    "sentence": "I'm learning how to make pizza."
  }
]
```

### GET /folders/{folder_id}/notes/{note_id}

Gets one active note.

Response:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pizza.",
  "created_at": "2026-05-07T10:30:00.000000",
  "updated_at": "2026-05-07T10:30:00.000000"
}
```

### PUT /folders/{folder_id}/notes/{note_id}

Request body:

```json
{
  "sentence": "I'm learning how to make pasta."
}
```

Updates a note sentence and rebuilds active relations connected to that note.

Response:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pasta.",
  "updated_at": "2026-05-07T10:40:00.000000"
}
```

### DELETE /folders/{folder_id}/notes/{note_id}

Soft deletes a note and relations/evidence connected to it.

Response:

```json
{
  "deleted": true
}
```

## Relations

### GET /folders/{folder_id}/relations

Lists active relations in a folder. This endpoint reads existing data and does
not recompute similarity or NLI.

Frontend behavior expectations:

- render relations efficiently
- support graph or list visualization
- avoid recomputing relations client-side
- support empty relation states

Response:

```json
[
  {
    "relation_id": "33333333-3333-3333-3333-333333333333",
    "note_1_id": "22222222-2222-2222-2222-222222222222",
    "note_1_sentence": "I'm learning how to make pizza.",
    "note_2_id": "44444444-4444-4444-4444-444444444444",
    "note_2_sentence": "I am studying pizza cooking."
  }
]
```

### GET /folders/{folder_id}/relations/{relation_id}/evidence

Gets latest active evidence for a relation.

Response:

```json
{
  "relation_id": "33333333-3333-3333-3333-333333333333",
  "relation_type": "related_entailment",
  "similarity_score": 0.9044219255447388,
  "nli_label": "entailment",
  "words_overlap": [
    "learning",
    "pizza"
  ],
  "similar_words": [
    {
      "word1": "make",
      "word2": "cooking",
      "score": 0.79
    }
  ]
}
```

### GET /folders/{folder_id}/relations/{relation_id}/explanation

Reads an existing explanation. This endpoint is read-only: it does not generate
or write anything.

Response when explanation exists:

```json
{
  "relation_id": "33333333-3333-3333-3333-333333333333",
  "explanation": "Both notes describe learning about preparing food."
}
```

Response when no explanation exists:

```json
{
  "detail": "Explanation not found."
}
```

### POST /folders/{folder_id}/relations/{relation_id}/explanation

Creates an explanation if none exists. If an explanation already exists, it
returns the existing explanation and does not regenerate or replace it.

Response:

```json
{
  "relation_id": "33333333-3333-3333-3333-333333333333",
  "explanation": "Both notes describe learning about preparing food."
}
```

Status behavior:

| Status | Meaning |
| --- | --- |
| `201 Created` | Explanation was generated and saved. |
| `200 OK` | Explanation already existed and was returned. |
| `400 Bad Request` | Latest evidence exists but `llm_payload` is not usable. |
| `404 Not Found` | Folder, relation, evidence, or explanation was not found. |

## Error Handling Expectations

Frontend code should normalize backend errors into consistent UI behavior.

Recommended handling:

| Status | Frontend Behavior |
| --- | --- |
| `400` | Show actionable validation or request error. |
| `401` | Reset auth state or redirect to login flow. |
| `403` | Show permission error UI. |
| `404` | Show not-found UI state. |
| `422` | Show field validation feedback. |
| `500` | Show retryable server error state. |
| `503` | Show temporary unavailable state. |

Do not expose raw backend stack traces to users.

## Common Errors

Missing or invalid API key:

```json
{
  "detail": "Invalid API key."
}
```

Missing resource:

```json
{
  "detail": "Folder not found."
}
```

Validation errors are generated by FastAPI/Pydantic and return `422`.

## Frontend Integration Principles

- Keep API access centralized.
- Use shared typed models.
- Avoid duplicating backend logic.
- Prefer predictable API state handling.
- Keep UI resilient to slow or failed requests.
- Support loading, empty, and error states consistently.
- Keep frontend behavior aligned with backend contracts.