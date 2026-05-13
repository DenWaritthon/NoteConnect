# Phase 4: Notes CRUD & Editor Experience

## Goal

Make note-taking fast, clear, and reliable by supporting the full core note lifecycle.

## Main Work

- Build `/folders/:folderId/notes/:noteId`.
- Support note creation.
- Support note editing.
- Support note deletion.
- Implement a clear save or auto-save flow.
- Add validation feedback.
- Prevent duplicate submissions.
- Refresh notes and relations after creating, updating, or deleting a note.
- Display note metadata and relation entry points.
- Support keyboard accessibility in editor workflows.

## Expected Outcomes

- Users can create, edit, delete, and open note details.
- Note mutations do not leave relation or graph data stale.
- The editor clearly communicates saving, saved, and error states.
- Page logic remains workflow composition instead of becoming a large component.

## Out of Scope

- Rich text editing.
- Markdown support.
- Search or tags.
