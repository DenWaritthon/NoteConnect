# NoteConnect User Guide

This guide explains how to use the NoteConnect frontend.

## Open the App

Open the deployed app in a browser:

```text
http://your-server-ip:3000
```

If the app is behind a domain or reverse proxy, open that domain instead.

## Main Pages

### Home

Path:

```text
/
```

The home page introduces NoteConnect and includes an `Open Note` button.

Click `Open Note` to go to the notes workspace.

### Notes

Path:

```text
/notes
```

The notes page is the main workspace for folders, notes, and relation graphs.

## Folder Workflow

### Create a Folder

1. Open `/notes`.
2. Click the folder button in the sidebar.
3. A new folder is created and selected.

### Select a Folder

Click a folder name in the sidebar.

The editor loads that folder's notes from the backend.

### Rename a Folder

1. Click the folder title at the top of the editor.
2. Type the new name.
3. Click outside the title field.

The app saves the new folder name when the title field loses focus.

### Refresh a Folder

Click the refresh button in the editor toolbar.

This reloads the selected folder and its notes from the backend.

### Delete a Folder

Click the delete button at the bottom of the editor.

The selected folder is deleted from the backend.

## Note Workflow

### Write Notes

Type notes in the editor.

Each non-empty line becomes one saved note.

Example:

```text
Machine learning helps identify patterns.
Graph views make relationships easier to understand.
Short notes are easier to connect.
```

This creates three notes.

### Save Notes

Notes are saved automatically after you pause typing.

Notes also save when:

- You press `Enter`.
- You click outside the editor.
- You open the relation graph.

### Edit Notes

Change a line in the editor.

The app updates the matching note on the backend.

### Delete Notes

Remove a line from the editor.

The app deletes the matching note from the backend during save.

## Relation Graph

### Open the Graph

Click `Relation`.

The app saves any unsaved note changes, loads relation data from the backend, and opens the graph modal.

### Use the Graph

The graph shows notes as nodes and relationships as edges.

You can use the graph to inspect how notes are connected inside the selected folder.

### Relation Loading

If relation data is loading, the graph modal shows a loading message.

If relation data cannot load, the graph modal shows an error message.

## Fullscreen Editing

Click the fullscreen button in the editor toolbar to hide the sidebar and focus on the current folder.

Click it again to return to the normal layout.

## Common Problems

### Missing API Key

If the notes page shows a missing API key error, the server is missing `API_SECRET_KEY`.

Fix:

```env
API_SECRET_KEY=your_api_secret_key
```

Then rebuild and restart the app.

### Folders or Notes Do Not Load

Check that:

- The backend API is running.
- `NOTE_CONNECT_API_BASE_URL` points to the backend.
- The API key and header name match the backend configuration.

### Graph Does Not Show Relations

Check that:

- The selected folder has at least two notes.
- The backend has generated relation data.
- The relation endpoint is reachable.
