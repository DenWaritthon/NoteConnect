# Phase 3: Folder & Workspace MVP

## Goal

Build the core workflow that lets users start managing their NoteConnect workspace.

## Main Work

- Build `/folders` as the main note workspace.
- Support folder create, rename, and delete actions.
- Build `/folders/:folderId` for the folder workspace.
- Display folder metadata.
- Display the notes list in the workspace.
- Display note and relation counts in the folder detail area.
- Add a graph access button.
- Refresh folder data after mutations.
- Support loading, empty, error, and success states.
- Build a workspace folder rail that works on desktop and mobile.

## Expected Outcomes

- Users can create and open folders.
- Users can view a folder workspace with key information.
- The workspace structure is ready for the note editor, relations, and graph.
- `/folders` and `/folders/:folderId` use the service layer for data access.

## Out of Scope

- A full note editor.
- Relation detail pages.
- Interactive graph visualization.

## Implementation Completed

- Added `/folders` as the main Note Workspace page.
- Added folder list loading, empty, error, and success states.
- Added a left-side folder rail that lists all folders.
- Added a create-folder dialog with a close button for both empty and existing-folder states.
- Added create, edit, open, and delete folder actions.
- Added always-editable folder name and description fields in the workspace card, with Save confirming changes.
- Added `/folders/:folderId` as a deep link into the same workspace layout.
- Switched folder selection to client-side state with History API URL updates so changing folders does not trigger a full route navigation.
- Smoothed folder switching by keeping the workspace card mounted during data refreshes instead of replacing it with a full loading state.
- Added optimistic folder selection so the selected folder and URL update immediately while last-opened metadata refreshes in the background.
- Loaded folder metadata, notes, and relations through the shared API service layer.
- Added read-only notes display in the same card as folder details.
- Added note and relation counts to the top-right area of the folder detail card.
- Kept last-opened metadata under the folder name in the left rail and removed it from the workspace card.
- Added the graph access point from the workspace.
- Moved Save, Delete, and Open graph into the top toolbar.
- Reduced the toolbar density and made Save visually primary only when unsaved folder changes exist.
- Combined folder details and notes into a single Apple Notes-style workspace card.
- Replaced the text separator with a horizontal divider line.
- Reduced the folder description field height so it fits the detail content more closely.
- Simplified note display so each note appears as one continuous line item without per-note dividers or metadata.
- Added a placeholder route for `/folders/:folderId/graph` so navigation does not fall into a 404 before the graph phase.
- Removed the global workspace sidebar from Home and Workspace so the Workspace left side is dedicated to folders.
- Updated the theme control to use a compact label-plus-track toggle with the thumb constrained inside the track.
- Stabilized the theme toggle during route changes by applying the saved theme before hydration and driving the thumb position from `html[data-theme]`.
- Removed route-change flicker from the theme label by initializing the visible label from the current client theme instead of a temporary light default.
- Removed the theme toggle hydration mismatch by keeping server and client markup stable while CSS reflects the active `html[data-theme]`.
- Removed refresh-time theme toggle jitter by enabling thumb animation only after the client confirms the theme is ready.
- Persisted the selected theme to a server-readable cookie so refreshes render the correct light or dark theme before client hydration.
- Removed route-change flicker from the Save action by treating folder edits as dirty only after the edit fields are synced to the active folder.
- Clarified that API Status is a development-only readiness check.
- Removed phase scaffolding from the visible web UI, including demo graph cards, environment display, future-only sidebar links, and the unfinished settings entry.
- Updated the Next proxy route to read `API_BASE_URL`, attach `API_SECRET_KEY`, and use `API_KEY_HEADER_NAME` for protected backend endpoints.

## Result

- Users can open `/folders` and see the latest opened folder when folders exist.
- Users can create a folder from a dialog, edit its name and description inline, save changes, delete it, and open folders from the left rail.
- Users can switch folders from the left rail without a page reload, full route transition, or workspace-card remount flicker.
- Users can open `/folders/:folderId` and see the same workspace layout with that folder selected.
- Users can see folder metadata, notes, note counts, relation counts, and left-rail last-opened metadata.
- If a workspace has no notes or relations, the UI shows explicit empty states.
- The graph button opens a planned-feature page instead of a missing route.
- The visible navigation now focuses on usable Phase 3 workflows instead of future-phase placeholders.
- Protected folder endpoints are reached through the same-origin Next proxy without exposing the API secret to the browser bundle.

## Verification

- `npm run lint` passed.
- `npm run build` passed.
- Local proxy verification returned `200 OK` for `GET /api/backend/folders`.
- Browser verification opened `/folders`, showed the latest opened folder, confirmed the create-folder dialog opens and closes with the close button, and confirmed the single-card workspace layout renders notes and counts.
- Browser verification confirmed folder switching updates the workspace without a full page reload, keeps the workspace card mounted, and renders the selected folder details after the smooth refresh.
- Theme verification confirmed the dark-mode toggle thumb keeps its position while moving between Home and Workspace.
- Browser verification confirmed Home and Workspace route changes no longer flash a primary Save button or overlapping Light/Dark theme text in dark mode.
- Browser verification confirmed the theme toggle no longer raises a hydration mismatch overlay in dark mode.
- Browser verification confirmed repeated page refreshes keep the dark-mode theme toggle stable without label overlap or hydration overlays.
- Browser verification confirmed repeated refreshes in both light and dark modes keep `html[data-theme]` aligned with the saved theme before interaction.
