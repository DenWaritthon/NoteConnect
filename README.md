# NoteConnect

NoteConnect Frontend is a Next.js note-taking app that lets you create folders, write notes one sentence per line, and view relationships between notes as an interactive graph.

This README is for running the project locally.

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

The JavaScript dependency list is managed in:

- `frontend/package.json`
- `frontend/package-lock.json`

The root `requirements.txt` is only a reference list for this project. The app itself is a Next.js frontend, so use `npm install` inside `frontend`.

## Environment Setup

Create a local environment file:

```bash
cd frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NOTE_CONNECT_API_BASE_URL=http://127.0.0.1:6550
API_SECRET_KEY=your_api_secret_key
API_KEY_HEADER_NAME=NoteConnect-API-Key
```

Environment variables:

- `NOTE_CONNECT_API_BASE_URL`: backend API base URL. Defaults to `http://127.0.0.1:6550`.
- `API_SECRET_KEY`: API key sent from the frontend proxy to the backend.
- `NOTE_CONNECT_API_KEY`: alternative API key variable if `API_SECRET_KEY` is not set.
- `API_KEY_HEADER_NAME`: header name used for the API key. Defaults to `X-API-Key`.

## Run Locally

Start the local development server:

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

Run these inside the `frontend` directory.

Start the development server:

```bash
npm run dev
```

Build the production app:

```bash
npm run build
```

Start the production server after a successful build:

```bash
npm run start
```

Run ESLint:

```bash
npm run lint
```

## Project Structure

```text
NoteConnect/
+-- frontend/
|   +-- docs/
|   +-- public/
|   +-- src/
|   |   +-- app/
|   |   |   +-- api/backend/[...path]/route.ts
|   |   |   +-- notes/page.tsx
|   |   |   +-- page.tsx
|   |   +-- components/
|   |   +-- lib/
|   |   +-- store/
|   +-- package.json
|   +-- package-lock.json
+-- requirements.txt
+-- README.md
```

## More Documentation

Additional documentation is available in `frontend/docs`:

- `phase1-5.md`: phase update for sessions 1-5
- `file_structure.md`: frontend file structure
- `user_guide.md`: app usage guide
- `server_deploy.md`: server deployment guide with PM2

## Troubleshooting

If the notes page shows a missing API key error, make sure `API_SECRET_KEY` is set in `frontend/.env.local`.

If folders or notes do not load, make sure the backend is running and `NOTE_CONNECT_API_BASE_URL` points to the correct backend URL.

If dependencies fail to install, delete `frontend/node_modules`, keep `frontend/package-lock.json`, and run:

```bash
npm install
```
