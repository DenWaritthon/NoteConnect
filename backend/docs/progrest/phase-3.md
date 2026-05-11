# Phase 3: Explanation Pipeline

Status: Complete and verified through API, service, database, and model
integration testing.

Phase 3 focuses on building the explanation workflow for note relations until it
can be connected cleanly to the API.

## Goal

Create a production-ready explanation system that can generate, store, and
expose explanations for existing note relations without recomputing similarity
or NLI inside API read endpoints.

## Implemented Focus

- Added service-layer explanation workflow.
- Added production explanation generator based on the POC approach.
- Explanation generation uses `note_relation_evidence.llm_payload` as input.
- Stores generated explanation text in `note_relation_evidence.explanation`.
- Updates relation `process_status` to `add_explanation` when explanation data is added.
- Added relation explanation API endpoints.
- Keeps explanation generation out of API route handlers.
- Reuses existing relation/evidence records instead of recomputing similarity or NLI.

## Expected System Flow

```text
Existing relation
        |
        v
Load latest relation evidence
        |
        v
Build explanation prompt/input
        |
        v
Generate explanation
        |
        v
Store explanation in note_relation_evidence
        |
        v
Update relation process_status
        |
        v
Expose through API
```

## API Behavior

```text
GET  /folders/{folder_id}/relations/{relation_id}/explanation
POST /folders/{folder_id}/relations/{relation_id}/explanation
```

- `GET` reads an existing explanation only.
- `GET` returns `404 Explanation not found.` when no explanation exists.
- `POST` creates an explanation when one does not exist.
- `POST` returns the existing explanation when one already exists.
- There is no regenerate or replace endpoint.
- API response includes only `relation_id` and `explanation`.

## Verification

Completed checks:

```bash
cd backend
.venv/bin/python -m compileall src main.py tests
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/run_phase1_3_real_test.py
```

Automated service and API contract tests now cover:

- `GET /explanation` returns `404` when no explanation exists.
- First `POST /explanation` returns `201`.
- Repeated `POST /explanation` returns `200` and the existing explanation.
- `GET /explanation` returns the stored explanation after creation.
- `GET` does not call the explanation generator when explanation is missing.
- `POST` stores explanation text and updates relation status to `add_explanation`.
- Real integration test verifies explanation generation, repeated POST behavior,
  later GET behavior, DB explanation persistence, and relation status update.

## Progress

```text
Phase 3 Explanation Planning:       100%
Phase 3 Service Workflow:           100%
Phase 3 Database Integration:       100%
Phase 3 API Integration:            100%
Phase 3 Verification:               100%
```

Overall Phase 3 progress:

```text
100%
```

## Completion Notes

- `GET /explanation` missing path returns `404`.
- First `POST /explanation` generates, saves, and returns `201`.
- Repeated `POST /explanation` returns the existing explanation with `200`.
- Later `GET /explanation` returns the stored explanation.
- `note_relation_evidence.explanation` and `note_relation.process_status = add_explanation`
  were verified directly through the integration test.
- Startup/loading strategy optimization moves to Phase 4.
