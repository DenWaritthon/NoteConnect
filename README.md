# NoteConnect

NoteConnect Frontend is a Next.js note-taking app that lets you create folders, write notes one sentence per line, and view relationships between notes as an interactive graph.

## Features

- Landing page for the NoteConnect app
- Folder-based note organization
- Note editor where each saved line becomes one note
- Backend API proxy through the Next.js app
- Interactive relation graph using React Flow
- Tailwind CSS styling with Framer Motion animations

## Requirements

Install these before running the project:

- Node.js 20 or newer
- npm
- A running NoteConnect backend API, if you want folder, note, and relation data to load

## Install Dependencies

From the project root, install the frontend dependencies:

```bash
cd frontend
npm install
```

The actual JavaScript dependency list is managed in:

- `frontend/package.json`
- `frontend/package-lock.json`

The root `requirements.txt` is only a reference list for this project. The app itself is a Next.js frontend, so use `npm install` inside `frontend`.

## Environment Setup

Create a local environment file:

```bash
cd frontend
cp .env.local.example .env.local
```

If `.env.local.example` does not exist, create `frontend/.env.local` manually:

```env
NOTE_CONNECT_API_BASE_URL=http://127.0.0.1:6550
API_SECRET_KEY=your_api_key_here
API_KEY_HEADER_NAME=X-API-Key
```

Environment variables:

- `NOTE_CONNECT_API_BASE_URL`: backend API base URL. Defaults to `http://127.0.0.1:6550`.
- `API_SECRET_KEY`: API key sent from the frontend proxy to the backend.
- `NOTE_CONNECT_API_KEY`: alternative name for the API key if `API_SECRET_KEY` is not set.
- `API_KEY_HEADER_NAME`: header name used for the API key. Defaults to `X-API-Key`.

## Run the App

Start the development server:

```bash
cd frontend
npm run dev
```

Open the app at:

```text
http://localhost:3000
```

Main pages:

- `/`: landing page
- `/notes`: note editor and graph view

## How to Use

1. Open `http://localhost:3000`.
2. Click `Open Note`.
3. Create a folder with the folder button.
4. Rename the folder by editing the title at the top of the editor.
5. Write notes in the editor, one sentence per line.
6. Click `Relation` to open the graph view for the current folder.
7. Use the refresh, fullscreen, and delete buttons as needed.

## Available Scripts

Run these inside the `frontend` directory:

```bash
npm run dev
```

Starts the development server.

```bash
npm run build
```

Builds the production app.

```bash
npm run start
```

Starts the production server after a successful build.

```bash
npm run lint
```

Runs ESLint.

## Project Structure

```text
NoteConnect/
+-- frontend/
|   +-- app/
|   |   +-- page.tsx
|   |   +-- notes/page.tsx
|   |   +-- api/backend/[...path]/route.ts
|   +-- components/
|   +-- lib/
|   +-- public/
|   +-- store/
|   +-- package.json
|   +-- package-lock.json
+-- requirements.txt
+-- README.md
```
## Troubleshooting

If the notes page shows a missing API key error, add `API_SECRET_KEY` to `frontend/.env.local`.

If folders or notes do not load, make sure the backend is running and `NOTE_CONNECT_API_BASE_URL` points to the correct backend URL.

If dependencies fail to install, delete `frontend/node_modules`, keep `frontend/package-lock.json`, and run:

```bash
npm install
```
