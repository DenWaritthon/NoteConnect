# Phase 3: Explanation Pipeline

Status: Complete and verified through API, service, database, and model
integration testing.

## Goal

Add relation explanation generation to the production backend without importing
from the POC directly. The explanation pipeline must use stored
`note_relation_evidence.llm_payload` as its input and expose a simple API.

## What Was Built

- Added production `ExplanationGenerator`.
- Added `ExplanationService` for get-or-create explanation behavior.
- Added `llm_payload` builder for new relation evidence.
- Stored explanation text in `noteconnect_note_relation_evidence.explanation`.
- Updated relation `process_status` to `add_explanation` after explanation is
  added.
- Added explanation endpoints under the relation router:
  - `GET /folders/{folder_id}/relations/{relation_id}/explanation`
  - `POST /folders/{folder_id}/relations/{relation_id}/explanation`
- Kept `GET` read-only.
- Kept `POST` as get-or-create.
- Removed regenerate/replace behavior from the API design.
- Added lazy explanation model loading support later used by deployment work.

## Result

Phase 3 added a complete explanation workflow:

- existing explanation can be read
- missing explanation returns `404` on `GET`
- first `POST` generates and stores explanation
- repeated `POST` returns existing explanation
- no API route recomputes similarity or NLI
- explanation response contains only `relation_id` and `explanation`

This made explanation generation available through the production API while
keeping explanation input traceable to stored evidence.

## Verification Outcome

Verification passed with:

- compile checks
- service tests
- API contract tests
- real DB/model integration testing during development

Verified behavior:

- missing `GET /explanation` returns `404`
- first `POST /explanation` returns `201`
- repeated `POST /explanation` returns `200`
- stored explanation can be read by later `GET`
- explanation text is persisted in the database
- relation status changes to `add_explanation`

## Progress

```text
Overall Phase 3 progress: 100%
```
