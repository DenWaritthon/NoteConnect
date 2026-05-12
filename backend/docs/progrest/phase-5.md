# Phase 5: Internal Optimization

Status: Complete and verified on the internal/nohup server deployment.

## Goal

Improve observability, database performance readiness, and maintainability for
the internal/nohup deployment without changing API contracts or core relation
behavior.

## What Was Built

### Phase 5A: Logging Baseline

- Added `LOG_REQUESTS`.
- Added `SLOW_REQUEST_MS`.
- Added request logging middleware with method, path, status, and duration.
- Added timing logs for note creation, note update, relation rebuild, and
  explanation generation.
- Added explanation model load duration log.
- Avoided logging API secrets, embeddings, full payloads, and note text.

### Phase 5B: DB Index Baseline

- Added `backend/database/create_index.sql`.
- Added active folder ordering index.
- Added active notes by folder/created index.
- Added pgvector HNSW cosine index for note embeddings.
- Added active relations by folder/created index.
- Added active relation lookup indexes by `note_1_id` and `note_2_id`.
- Added latest active evidence lookup index by relation and created time.

The application does not apply indexes at runtime. Index SQL is handled
manually on the database server.

### Phase 5C: Clean Code

- Added shared constants for process statuses, LLM payload keys, and common
  service errors.
- Added `build_relation_llm_payload()` to keep explanation input shape in one
  place.
- Updated services to use shared constants and payload helper.
- Added unit coverage for payload builder and constants-backed status behavior.

## Result

Phase 5 made the internal deployment easier to observe and maintain:

- request latency is visible in logs
- slow requests can be identified
- model-heavy workflows have timing logs
- baseline database index SQL exists for current query patterns
- repeated string/status/payload logic is centralized
- API behavior stayed unchanged

## Verification Outcome

Verification passed:

- local compile check passed
- local unit tests passed with `Ran 25 tests, OK`
- deploy readiness checks passed
- Phase 5 deploy package was tested on the Ubuntu server
- server readiness checks passed
- `nohup` restart passed
- `/health` and `/ready` passed
- existing API CRUD workflow passed
- relation/evidence workflow passed
- explanation POST and repeated POST behavior passed
- cleanup and restart/recovery checks passed
- logs showed request/service timing without exposing sensitive payloads
- RAM/swap stayed acceptable for the tested workload

## Progress

```text
Overall Phase 5 progress: 100%
```
