# Phase 5: Internal Optimization

Status: Complete and verified on the internal/nohup server deployment.

Phase 5 improves observability and database performance for the internal/nohup
deployment target without changing API contracts, relation behavior, model
choices, or public deployment scope.

## Scope

- Add production-safe request logging.
- Add timing logs for model-heavy service workflows.
- Add a database index baseline for current query patterns.
- Keep schema changes out of application runtime.
- Keep tests fast and server-safe.

## Phase 5A: Logging Baseline

Implemented:

- Added `LOG_REQUESTS` config.
- Added `SLOW_REQUEST_MS` config.
- Added request logging middleware with method, path, status, and duration.
- Added note pipeline timing logs for embedding, relation rebuild, create note,
  and update note.
- Added explanation timing logs for existing explanation return and new
  generation.
- Added explanation model load duration log.
- Avoided logging API secrets, embeddings, full payloads, or note text.

## Phase 5B: DB Index Baseline

Implemented:

- Added `backend/database/create_index.sql`.
- Added active folder ordering index.
- Added active notes by folder/created index.
- Added pgvector HNSW cosine index for note embeddings.
- Added active relations by folder/created index.
- Added active relation lookup indexes by `note_1_id` and `note_2_id`.
- Added latest active evidence lookup index by relation and created time.

The application does not create indexes at runtime. Indexes must be applied
manually on the database server.

## Phase 5C: Clean Code

Implemented:

- Added shared constants for process status values, LLM payload keys, and common
  service error messages.
- Replaced hardcoded `relation_confirmed` and `add_explanation` service writes
  with constants.
- Replaced repeated service-layer not-found and payload validation messages with
  constants.
- Added `build_relation_llm_payload()` to keep the AGENTS.md explanation input
  shape in one place.
- Updated the note relation pipeline to call the shared payload builder.
- Kept API response contracts, database writes, relation behavior, and model
  behavior unchanged.
- Added unit coverage for the payload builder and constants-backed status
  behavior.

## Progress

```text
Phase 5A Logging Baseline: 100%
Phase 5B DB Index Baseline: 100%
Phase 5C Clean Code:        100%
Phase 5D Verification:      100%
```

Overall Phase 5 progress:

```text
100%
```

## Phase 5D: Verification

Verified:

- Local compile check passed.
- Local unit tests passed with `Ran 25 tests, OK`.
- `check_deploy_ready.py` passed.
- Phase 5 deploy package was copied to the Ubuntu server.
- `database/create_index.sql` was applied successfully.
- Server readiness checks passed.
- `nohup` service restarted successfully.
- `/health` returned `ok`.
- `/ready` returned `database: ok`.
- Request logs include method, path, status, and duration.
- Service timing logs appear for note/relation/explanation workflows.
- Logs do not expose API secrets, embeddings, full payloads, or note text.
- Existing API CRUD workflow still passed.
- Relation/evidence workflow still passed.
- Explanation POST and repeated POST behavior still passed.
- Cleanup and restart/recovery checks passed.
- RAM/swap stayed acceptable for the tested workload.

## Future Work

- Optional deeper `EXPLAIN ANALYZE` review with larger real datasets.
- Optional latency dashboards or log aggregation if the internal deployment
  grows beyond manual log inspection.
- Optional cleanups only when they reduce concrete duplication or operational
  risk.
