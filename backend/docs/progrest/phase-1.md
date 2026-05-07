# Phase 1: Core Production Pipeline

Status: Functionally complete and tested with the real PostgreSQL database.

Phase 1 moved the note relationship workflow from `backend/poc/` into
production-ready backend code under `backend/src/`. The POC remains available as
a workflow reference and was not modified.

## Scope

- Build reusable backend core code without FastAPI routes.
- Use PostgreSQL with pgvector for embedding storage and similarity search.
- Use psycopg3 for database access.
- Keep SQL inside the Data layer.
- Keep AI and business logic inside the Service layer.
- Support terminal usage similar to the POC while writing to the real database.
- Use soft delete behavior for folders, notes, relations, and relation evidence.

## Implemented Structure

```text
backend/src/
  core/
    config.py
    database.py
  data/
    folder_repository.py
    note_repository.py
    relation_repository.py
    evidence_repository.py
    models.py
  services/
    folder_service.py
    note_service.py
    relation_service.py
    sentence_processor.py

backend/scripts/
  terminal_demo.py
  run_phase1_demo.py
```

## Implemented Features

- Central configuration loading from `backend/.env`.
- PostgreSQL connection and transaction helper with pgvector registration.
- Folder create, list, open, and soft delete.
- Note create, update, list, and soft delete.
- Embedding generation and pgvector Top-K similarity search.
- NLI relation classification.
- Relation persistence in `note_relation`.
- Evidence persistence in `note_relation_evidence`.
- Manual soft delete cascade for folder children.
- Terminal demo for manual testing against the real database.

## Verification

Completed checks:

```bash
backend/.venv/bin/python -m compileall backend/src backend/scripts
```

Manual verification with the real PostgreSQL database was completed and no
issues were found in the tested Phase 1 flows.

Verified flows:

- create folder
- add note
- save embedding
- pgvector similarity search
- create relation
- create relation evidence
- update note and rebuild related relation/evidence records
- delete note with soft delete behavior
- delete folder with soft delete behavior for child records
- use terminal demo against the real database

## Progress

```text
Phase 1 Core Structure:             95%
Phase 1 Database Layer:             95%
Phase 1 Service Pipeline:           95%
Phase 1 Folder/Note Soft Delete:    95%
Phase 1 Terminal Demo:              95%
Phase 1 Database Compliance:        95%
Phase 1 Documentation/Comments:     90%
Phase 1 End-to-end DB Verification: 95%
```

Overall Phase 1 progress:

```text
95%
```
