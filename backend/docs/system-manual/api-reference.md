# Backend API Reference

This document lists all current NoteConnect backend API endpoints.

Base URL for local development:

```text
http://127.0.0.1:8000
```

Protected endpoints require:

```http
X-API-Key: your-secret
```

The health endpoint is public.

## GET /health

Check whether the API is running.

Authentication: not required.

Request body: none.

Response example:

```json
{
  "status": "ok"
}
```

## POST /folders

Create a folder.

Authentication: required.

Request example:

```json
{
  "name": "Study Notes",
  "description": "Notes about learning and research"
}
```

Response example:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Study Notes",
  "created_at": "2026-05-07T10:00:00.000000"
}
```

## GET /folders

List active folders.

Authentication: required.

Request body: none.

Response example:

```json
[
  {
    "folder_id": "11111111-1111-1111-1111-111111111111",
    "name": "Study Notes",
    "last_open_at": "2026-05-07T10:10:00.000000"
  }
]
```

## GET /folders/{folder_id}

Get one active folder.

Authentication: required.

Request body: none.

Response example:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Study Notes",
  "description": "Notes about learning and research",
  "created_at": "2026-05-07T10:00:00.000000",
  "updated_at": "2026-05-07T10:20:00.000000",
  "last_open_at": "2026-05-07T10:10:00.000000"
}
```

## PATCH /folders/{folder_id}

Update folder name or description.

Authentication: required.

Request example, update only name:

```json
{
  "name": "Updated Study Notes"
}
```

Request example, update only description:

```json
{
  "description": "I'm updating only the description."
}
```

Request example, clear description:

```json
{
  "description": null
}
```

Response example:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "name": "Updated Study Notes",
  "description": "I'm updating only the description.",
  "updated_at": "2026-05-07T10:20:00.000000"
}
```

## PATCH /folders/{folder_id}/open

Open a folder and refresh `last_open_at`.

Authentication: required.

Request body: none.

Response example:

```json
{
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "last_open_at": "2026-05-07T10:25:00.000000"
}
```

## DELETE /folders/{folder_id}

Soft delete a folder and its child records.

Authentication: required.

Request body: none.

Response example:

```json
{
  "deleted": true
}
```

## POST /folders/{folder_id}/notes

Create a note in a folder.

Creating a note triggers embedding generation, pgvector similarity search, NLI
classification, and relation/evidence storage.

Authentication: required.

Request example:

```json
{
  "sentence": "I'm learning how to make pizza."
}
```

Response example:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pizza.",
  "created_at": "2026-05-07T10:30:00.000000"
}
```

## GET /folders/{folder_id}/notes

List active notes in a folder.

Authentication: required.

Request body: none.

Response example:

```json
[
  {
    "note_id": "22222222-2222-2222-2222-222222222222",
    "sentence": "I'm learning how to make pizza."
  }
]
```

## GET /folders/{folder_id}/notes/{note_id}

Get one active note in a folder.

Authentication: required.

Request body: none.

Response example:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pizza.",
  "created_at": "2026-05-07T10:30:00.000000",
  "updated_at": "2026-05-07T10:30:00.000000"
}
```

## PUT /folders/{folder_id}/notes/{note_id}

Update a note.

Updating a note soft deletes active relations connected to that note, replaces
the note sentence and embedding, and rebuilds relations.

Authentication: required.

Request example:

```json
{
  "sentence": "I'm learning how to make pasta."
}
```

Response example:

```json
{
  "note_id": "22222222-2222-2222-2222-222222222222",
  "folder_id": "11111111-1111-1111-1111-111111111111",
  "sentence": "I'm learning how to make pasta.",
  "updated_at": "2026-05-07T10:40:00.000000"
}
```

## DELETE /folders/{folder_id}/notes/{note_id}

Soft delete a note and relations connected to it.

Authentication: required.

Request body: none.

Response example:

```json
{
  "deleted": true
}
```

## GET /folders/{folder_id}/relations

List active relations in a folder.

Authentication: required.

Request body: none.

Response example:

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

## GET /folders/{folder_id}/relations/{relation_id}/evidence

Get the latest active evidence for a relation.

Authentication: required.

Request body: none.

Response example:

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

## Error Responses

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

Validation error responses are generated by FastAPI/Pydantic.
