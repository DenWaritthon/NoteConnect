# Phase 3: Explanation Pipeline

Status: Planned.

Phase 3 focuses on building the explanation workflow for note relations until it
can be connected cleanly to the API.

## Goal

Create a production-ready explanation system that can generate, store, update,
and expose explanations for existing note relations without recomputing
similarity or NLI inside API read endpoints.

## Planned Focus

- Design the explanation generation flow for existing relations.
- Decide the explanation input payload from stored relation evidence.
- Add a service-layer explanation workflow.
- Store generated explanation text in `note_relation_evidence.explanation`.
- Update relation `process_status` to `add_explanation` when explanation data is added.
- Add or extend API endpoints for requesting or reading explanation data.
- Keep explanation generation out of API route handlers.
- Reuse existing relation/evidence records instead of recomputing similarity or NLI.
- Add terminal or script-based testing before API integration if useful.

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

## Open Design Items

- Which model or service should generate explanations.
- Whether explanations should be generated automatically after relation creation or requested later.
- Whether explanation updates should create new evidence rows or update the latest evidence row.
- What response shape the explanation API should return.

## Progress

```text
Phase 3 Explanation Planning:       20%
Phase 3 Service Workflow:           0%
Phase 3 Database Integration:       0%
Phase 3 API Integration:            0%
Phase 3 Verification:               0%
```

Overall Phase 3 progress:

```text
5%
```
