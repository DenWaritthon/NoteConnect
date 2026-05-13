# Phase 3: Folder & Workspace MVP

## Goal

Build the core workflow that lets users start managing their NoteConnect workspace.

## Main Work

- Build `/folders` for viewing the folder list.
- Support folder create, rename, and delete actions.
- Build `/folders/:folderId` for the folder workspace.
- Display folder metadata.
- Display the notes list in the workspace.
- Display a basic relation summary.
- Add a graph access button.
- Refresh folder data after mutations.
- Support loading, empty, error, and success states.
- Build a sidebar that works on desktop and mobile.

## Expected Outcomes

- Users can create and open folders.
- Users can view a folder workspace with key information.
- The workspace structure is ready for the note editor, relations, and graph.
- `/folders` and `/folders/:folderId` use the service layer for data access.

## Out of Scope

- A full note editor.
- Relation detail pages.
- Interactive graph visualization.
