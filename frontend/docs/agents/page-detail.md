# Page Detail Guide

This document defines the responsibilities and workflows for frontend pages in NoteConnect.

Pages represent complete user-facing workflows, not only visual layouts.

---

## Global Page Expectations

Every page should:
- support loading, empty, success, and error states
- support responsive layouts
- support keyboard accessibility
- use the shared Service/API layer
- avoid duplicating backend logic
- avoid blank screens during async operations
- preserve useful URL state when appropriate

Pages should:
- compose features, components, hooks, and services
- avoid large reusable UI logic directly inside page files
- avoid raw `fetch` calls inside pages

---

## Folder List Page

Route: `/folders`

Purpose:
Manage and open folders.

Displays:
- folder list
- folder metadata
- create folder action

User Actions:
- create folder
- open folder
- rename folder
- delete folder

APIs:
- `GET /folders`
- `POST /folders`
- `PATCH /folders/{folder_id}`
- `DELETE /folders/{folder_id}`

---

## Folder Workspace Page

Route: `/folders/:folderId`

Purpose:
Main workspace for a selected folder.

Displays:
- folder metadata
- notes workspace
- relation summary
- graph access button

User Actions:
- create note
- edit note
- delete note
- open graph
- open relations

APIs:
- `GET /folders/{folder_id}`
- `GET /folders/{folder_id}/notes`
- `GET /folders/{folder_id}/relations`
- `POST /folders/{folder_id}/notes`

---

## Note Detail Page

Route: `/folders/:folderId/notes/:noteId`

Purpose:
Display note content and relationships.

Displays:
- note content
- note metadata
- relation summary
- evidence/explanation entry points

User Actions:
- edit note
- delete note
- open relation
- open explanation

APIs:
- `GET /folders/{folder_id}/notes/{note_id}`
- `PUT /folders/{folder_id}/notes/{note_id}`
- `DELETE /folders/{folder_id}/notes/{note_id}`

---

## Note Create / Edit Flow

Purpose:
Create or update notes.

Displays:
- note editor
- validation feedback
- save/cancel actions

User Actions:
- create note
- edit note
- submit changes
- cancel editing

APIs:
- `POST /folders/{folder_id}/notes`
- `PUT /folders/{folder_id}/notes/{note_id}`

Notes:
- Note creation triggers the backend relation pipeline.
- Do not duplicate relation logic in the frontend.

---

## Relations Page

Route: `/folders/:folderId/relations`

Purpose:
Display relationships between notes.

Displays:
- relation list
- relation metadata
- similarity score
- explanation/evidence actions

User Actions:
- open relation
- view evidence
- generate explanation

APIs:
- `GET /folders/{folder_id}/relations`
- `GET /folders/{folder_id}/relations/{relation_id}/evidence`
- `GET /folders/{folder_id}/relations/{relation_id}/explanation`
- `POST /folders/{folder_id}/relations/{relation_id}/explanation`

---

## Relation Detail Page

Route: `/folders/:folderId/relations/:relationId`

Purpose:
Display detailed relation information.

Displays:
- source note
- target note
- similarity score
- evidence
- explanation

User Actions:
- generate explanation
- open related notes
- view evidence

APIs:
- `GET /folders/{folder_id}/relations`
- `GET /folders/{folder_id}/relations/{relation_id}/evidence`
- `GET /folders/{folder_id}/relations/{relation_id}/explanation`
- `POST /folders/{folder_id}/relations/{relation_id}/explanation`

---

## Graph Page

Route: `/folders/:folderId/graph`

Purpose:
Visualize note relationships.

Displays:
- graph nodes
- graph edges
- selected node/relation detail

User Actions:
- zoom
- pan
- drag nodes
- open note detail
- open relation detail

APIs:
- `GET /folders/{folder_id}/notes`
- `GET /folders/{folder_id}/relations`

Notes:
- Keep graph rendering lightweight.
- Avoid recomputing relations in the frontend.

---

## Search Page

Route: `/search`

Purpose:
Search notes and relationships.

Displays:
- search input
- result list
- filters

User Actions:
- search
- filter results
- open result

APIs:
- Use existing backend search endpoints when available.

---

## Settings Page

Route: `/settings`

Purpose:
Manage frontend-visible user/application settings.

Displays:
- preferences
- theme settings
- save/cancel actions

User Actions:
- update preferences
- switch theme mode
- save changes

---

## Not Found Page

Purpose:
Handle invalid routes or missing resources.

Displays:
- not found message
- navigation back to workspace