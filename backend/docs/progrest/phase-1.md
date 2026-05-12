# Phase 1: Core Production Pipeline

Status: Complete and verified with the real PostgreSQL database.

## Goal

Build the production core backend pipeline from the POC workflow without adding
FastAPI yet. The target was to make folder/note/relation processing work against
PostgreSQL + pgvector through clean production layers.

## What Was Built

- Moved the core note relationship workflow into `backend/src/`.
- Added centralized `.env` configuration.
- Added psycopg3 database connection and transaction helpers.
- Added Data layer repositories for folders, notes, relations, and evidence.
- Added Service layer workflows for folder, note, relation, and sentence
  processing logic.
- Added embedding generation and pgvector Top-K similarity search.
- Added NLI-based relation classification.
- Added relation evidence writes with similarity score, NLI result, word
  overlap, similar words, and `llm_payload`.
- Added soft delete behavior for folders, notes, relations, and evidence.
- Kept `backend/poc/` as reference-only and did not import from it directly.

## Result

Phase 1 produced a working production core pipeline that can:

- create folders
- add/update/delete notes
- save note embeddings
- find similar notes inside the same folder
- create relation records
- create relation evidence records
- rebuild relations when a note changes
- soft delete data without hard deleting rows

The backend now has a reusable core that later phases can expose through an API.

## Verification Outcome

Verification passed with:

- compile checks
- unit tests
- real PostgreSQL database testing
- terminal-style workflow testing during development

The tested Phase 1 flows passed without blocking issues.

## Progress

```text
Overall Phase 1 progress: 100%
```
