# NoteConnect

## Phase 1: Core Production Pipeline

Status: Functionally complete and tested with the real PostgreSQL database.

Phase 1 moves the backend workflow from the proof-of-concept structure in
`backend/poc/` into production-ready reusable code under `backend/src/`.
The POC remains available as a workflow reference and was not modified.

### Scope

- Build the backend core without FastAPI routes yet.
- Use PostgreSQL with pgvector for note embedding storage and similarity search.
- Use psycopg3 for all database access.
- Keep SQL inside the Data layer.
- Keep AI and business logic inside the Service layer.
- Support terminal usage similar to the POC while writing to the real database.
- Use soft delete behavior for folders, notes, relations, and relation evidence.

### Implemented Structure

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

### Implemented Features

- Central configuration loading from `backend/.env`.
- PostgreSQL connection and transaction helper with pgvector registration.
- Folder lifecycle:
  - create folder
  - list folders
  - open folder and update `last_open_at`
  - soft delete folder
- Note lifecycle:
  - create note
  - update note
  - delete note by soft delete
  - list notes in a folder
- Relation pipeline:
  - generate sentence embedding
  - save embedding to `note.sentence_embedding`
  - search Top-K similar notes using pgvector cosine distance
  - filter by similarity threshold
  - run NLI with CrossEncoder
  - classify relation as `related_entailment`, `related_conflict`, or `related_semantic`
  - save relation in `note_relation`
  - save evidence in `note_relation_evidence`
- Evidence storage:
  - stores `similarity_score`
  - stores raw NLI model scores in `nli_score`
  - stores selected `nli_label`
  - stores `words_overlap`
  - stores `similar_words`
  - stores debug context in `llm_payload`
- Folder soft delete cascades manually through service logic:
  - folder
  - notes in the folder
  - relations in the folder
  - relation evidence connected to those relations
- Terminal demo for manual testing against the real database.
- Production code comments/docstrings for architecture boundaries and important rules.

### Terminal Demo

Run the Phase 1 terminal demo:

```bash
cd backend
.venv/bin/python scripts/terminal_demo.py
```

Supported actions:

```text
0  : quit
1  : create folder
2  : list folders
3  : open folder
4  : delete folder
5  : add note to current folder
6  : edit note
7  : delete note
8  : show notes in current folder
9  : show relations in current folder
10 : use demo notes in current folder
```

### Environment

Use `backend/.env.example` as the reference for required configuration.

Important model/database alignment:

- The database schema uses `VECTOR(768)`.
- The embedding model must return 768-dimensional vectors.
- The expected production embedding model is:

```text
sentence-transformers/all-mpnet-base-v2
```

### Verification

Completed checks:

```bash
backend/.venv/bin/python -m compileall backend/src backend/scripts
```

Manual verification with the real PostgreSQL database has been completed and no
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

### Current Progress

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

Phase 1 is functionally complete and ready to be used as the base for Phase 2:
FastAPI integration.
