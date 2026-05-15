# Frontend File Structure

This document explains the main files and folders inside the NoteConnect frontend.

## Root Frontend Directory

```text
frontend/
+-- src/
+-- public/
+-- docs/
+-- package.json
+-- package-lock.json
+-- next.config.js
+-- tailwind.config.ts
+-- tsconfig.json
+-- postcss.config.js
+-- eslint.config.mjs
+-- .env.example
```

## Important Files

### `package.json`

Defines the frontend package, dependencies, and npm scripts.

Main scripts:

```bash
npm run dev
npm run build
npm run start
npm run lint
```

### `.env.example`

Example environment file for local or server setup.

The app expects these production values:

```env
NOTE_CONNECT_API_BASE_URL=http://127.0.0.1:6550
API_SECRET_KEY=your_api_secret_key
API_KEY_HEADER_NAME=NoteConnect-API-Key
```

### `next.config.js`

Next.js configuration file.

### `tailwind.config.ts`

Tailwind CSS configuration for styling.

### `tsconfig.json`

TypeScript configuration.

## Source Directory

```text
src/
+-- app/
+-- components/
+-- lib/
+-- store/
```

## `src/app`

The `app` directory contains Next.js App Router pages, layout, global styles, and API routes.

```text
src/app/
+-- layout.tsx
+-- page.tsx
+-- globals.css
+-- favicon.ico
+-- notes/
|   +-- page.tsx
+-- api/
    +-- backend/
        +-- [...path]/
            +-- route.ts
```

### `src/app/layout.tsx`

Defines the root application layout and shared metadata.

### `src/app/page.tsx`

Landing page for NoteConnect.

Includes:

- App introduction.
- Feature highlights.
- Button navigation to `/notes`.
- Footer with project and developer details.

### `src/app/notes/page.tsx`

Main note-taking workspace.

Responsibilities:

- Load folders from the backend.
- Create folders.
- Select and open folders.
- Rename folders.
- Delete folders.
- Edit notes line by line.
- Autosave note changes.
- Open the relation graph modal.
- Load relation data for graph visualization.

### `src/app/api/backend/[...path]/route.ts`

Next.js backend proxy route.

Responsibilities:

- Receive frontend requests from `/api/backend/...`.
- Forward requests to `NOTE_CONNECT_API_BASE_URL`.
- Attach the configured API key header.
- Keep the API key server-side.
- Return backend responses to the frontend.

## `src/components`

Reusable UI components.

```text
src/components/
+-- Button.tsx
+-- GraphView.tsx
+-- Header.tsx
+-- Modal.tsx
+-- NoteItem.tsx
```

### `GraphView.tsx`

Interactive note relation graph built with React Flow.

It receives notes and relations, then renders nodes and edges.

### `Modal.tsx`

Reusable modal wrapper used by the relation graph view.

### `Header.tsx`

Shared header/navigation component.

### `Button.tsx`

Reusable button component.

### `NoteItem.tsx`

Small note item component.

## `src/lib`

Shared helper functions.

```text
src/lib/
+-- storage.ts
+-- utils.ts
```

### `storage.ts`

Local storage helpers for older or local note state.

### `utils.ts`

General utility helpers.

## `src/store`

```text
src/store/
+-- useNoteStore.ts
```

Contains a Zustand store for local note state. The current backend-connected notes page primarily uses API state directly, but this store remains available for local note workflows or future use.

## `public`

Static assets served by Next.js.

```text
public/
+-- Logo.svg
+-- file.svg
+-- globe.svg
+-- next.svg
+-- vercel.svg
+-- window.svg
```

## `docs`

Project documentation.

```text
docs/
+-- phase1-5.md
+-- file_structure.md
+-- user_guide.md
+-- server_deploy.md
```
