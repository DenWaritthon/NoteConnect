# Backend API Reference

This document describes all current NoteConnect backend API endpoints.

Local base URL:

```text
http://127.0.0.1:6550
```

Internal server base URL:

```text
http://127.0.0.1:6550
```

Protected endpoints require:

```http
X-API-Key: your-secret
```

`GET /health` and `GET /ready` are public.

## Curl Variables

For shorter examples:

```bash
API=http://127.0.0.1:6550
KEY=your-secret
```

When JSON contains apostrophes such as `I'm`, use escaped double quotes or a
JSON file. Do not wrap the whole JSON payload in single quotes.

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

## Health

### GET /health

Checks whether the API process is alive.

```bash
curl "$API/health"
```

Response:

```json
{
  "status": "ok"
}
```

### GET /ready

Checks whether the API is ready to serve. When `READY_CHECK_DATABASE=true`, it
also verifies database connectivity. The response also reports whether the AI
models are ready for the current process.

```bash
curl "$API/ready"
```

Response:

```json
{
  "status": "ready",
  "database": "ready",
  "explanation_load_mode": "lazy",
  "model_verified_loadable": true,
  "embedding_model_status": "loaded",
  "nli_model_status": "loaded",
  "explanation_model_status": "not_loaded"
}
```

Field notes:

| Field | Meaning |
| --- | --- |
| `database` | `ready` when DB check passes, or `skipped` when `READY_CHECK_DATABASE=false`. |
| `model_verified_loadable` | `true` only when embedding, NLI, and explanation model checks pass. |
| `embedding_model_status` | `loaded` when the shared embedding model is resident. |
| `nli_model_status` | `loaded` when the shared NLI model is resident. |
| `explanation_model_status` | `loaded` in `startup` mode; usually `not_loaded` in `lazy` mode after readiness verifies and unloads it. |

If the database check fails, the endpoint returns `503` with:

```json
{"detail": "Database is not ready."}
```

If the model check fails, the endpoint returns `503` with:

```json
{"detail": "Model is not ready."}
```

## Folders

### POST /folders

Creates a new folder. `description` is optional.

```bash
curl -X POST "$API/folders" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Study Notes\",\"description\":\"Learning notes\"}"
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

```bash
curl "$API/folders" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111" \
  -H "X-API-Key: $KEY"
```

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

Updates folder `name`, `description`, or both. Partial update is supported.
Sending `{"description": null}` clears the description.

```bash
curl -X PATCH "$API/folders/11111111-1111-1111-1111-111111111111" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated Study Notes\"}"
```

```bash
curl -X PATCH "$API/folders/11111111-1111-1111-1111-111111111111" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"description\":\"I'm updating the description.\"}"
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

```bash
curl -X PATCH "$API/folders/11111111-1111-1111-1111-111111111111/open" \
  -H "X-API-Key: $KEY"
```

Response:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "last_open_at": "2026-05-07T10:25:00.000000"
}
```

### DELETE /folders/{folder_id}

Soft deletes the folder, child notes, child relations, and child evidence.

```bash
curl -X DELETE "$API/folders/11111111-1111-1111-1111-111111111111" \
  -H "X-API-Key: $KEY"
```

Response:

```json
{
  "deleted": true
}
```

## Notes

### POST /folders/{folder_id}/notes

Creates a note and runs the relation pipeline:

```text
embedding -> pgvector similarity search -> NLI -> relation/evidence write
```

```bash
curl -X POST "$API/folders/11111111-1111-1111-1111-111111111111/notes" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pizza.\"}"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111/notes" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111/notes/22222222-2222-2222-2222-222222222222" \
  -H "X-API-Key: $KEY"
```

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

Updates a note sentence and rebuilds active relations connected to that note.

```bash
curl -X PUT "$API/folders/11111111-1111-1111-1111-111111111111/notes/22222222-2222-2222-2222-222222222222" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"sentence\":\"I'm learning how to make pasta.\"}"
```

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

```bash
curl -X DELETE "$API/folders/11111111-1111-1111-1111-111111111111/notes/22222222-2222-2222-2222-222222222222" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111/relations" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111/relations/33333333-3333-3333-3333-333333333333/evidence" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl "$API/folders/11111111-1111-1111-1111-111111111111/relations/33333333-3333-3333-3333-333333333333/explanation" \
  -H "X-API-Key: $KEY"
```

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

```bash
curl -X POST "$API/folders/11111111-1111-1111-1111-111111111111/relations/33333333-3333-3333-3333-333333333333/explanation" \
  -H "X-API-Key: $KEY"
```

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
