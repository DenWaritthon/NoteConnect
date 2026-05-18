# NoteConnect

NoteConnect is a short-note web application that helps users capture small pieces
of information and automatically discover relationships between notes. The
system visualizes those relationships as an interactive graph so users can
understand how their ideas connect.

## Demo

[Watch Demo Video](./Demo.mp4)

## What Is NoteConnect?

NoteConnect is designed for users who write many short notes and want to see how
those notes relate to each other. Instead of keeping notes as isolated text, the
system analyzes note content and creates relationship links between relevant
notes.

## Problem

Traditional note-taking tools usually store information as separate notes. This
makes it difficult to see connections between ideas, track related topics, or
understand the bigger picture of collected information.

NoteConnect addresses this by automatically analyzing note similarity and showing
connected notes in a relationship graph.

## Scope

### What The System Can Do

- Create, edit, and delete short notes.
- Organize notes into folders or boards.
- Treat each line of text as one note.
- Analyze relationships between notes automatically.
- Display note relationships as an interactive graph.
- Show relation evidence such as similarity score, overlapping words, similar
  concepts, and explanation payload.
- Optionally generate explanations for why two notes are related.
- Store notes, relationships, and analysis evidence in PostgreSQL.

### Current Limitations

- Supports English text only.
- Relationships are generated automatically and cannot be manually edited by
  users.
- No login system or per-user data separation.
- Relationship analysis only works on notes stored inside the system.
- The system may not understand deep implied context that is not clearly written
  in the note.

## Key Features

- Short-note editor
- Folder-based note organization
- Automatic relationship discovery
- Interactive relationship graph
- Relation detail view
- AI-assisted explanation generation

## How It Works

1. The user writes notes in the frontend.
2. Each note is sent to the backend through the API.
3. The backend converts note text into sentence embeddings.
4. PostgreSQL with pgvector searches for similar notes.
5. NLI classification confirms whether notes are meaningfully related.
6. Relationship evidence is stored in the database.
7. The frontend displays notes and relationships as a graph.

## Tech Stack Overview

### Frontend

- Next.js
- React
- Tailwind CSS
- xyflow / React Flow

More details: [Frontend README](./frontend/README.md)

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- PostgreSQL
- pgvector
- Sentence Transformers
- Natural Language Inference model
- Optional LLM explanation generation

More details: [Backend README](./backend/README.md)

## Documentation

- [Frontend Documentation](./frontend/README.md)
- [Frontend User Guide](./frontend/docs/user_guide.md)
- [Frontend File Structure](./frontend/docs/file_structure.md)
- [Frontend Server Deploy Guide](./frontend/docs/server_deploy.md)
- [Backend Documentation](./backend/README.md)
- [Backend API Reference](./backend/docs/system-manual/api-reference.md)
- [Backend System Architecture](./backend/docs/system-manual/system-architecture.md)
- [Backend Database Detail](./backend/docs/system-manual/database-detail.md)
- [Backend Test Detail](./backend/docs/system-manual/test-detail.md)

## Team

This project was developed for FRA502 Web Programming.

| Name | Responsibility |
| --- | --- |
| Chawaphon Wachiraniramit | Frontend development, UI development, web page detail, real-time frontend state update, frontend-backend integration, deployment |
| Waritthorn Kongnoo | Backend development, sentence embeddings, note comparison system, explanation generation, backend management, API development, database development, frontend-backend integration, deployment |
