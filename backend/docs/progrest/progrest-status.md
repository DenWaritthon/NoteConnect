# Backend Progress Status

This document summarizes the current backend phase status. For implementation
detail, open the linked phase document.

## Summary

The backend is complete for the current internal/nohup deployment target. It can
store folders and notes, build note relations with PostgreSQL + pgvector + NLI,
serve the workflow through FastAPI, generate relation explanations, and run on
an internal Ubuntu server with readiness checks, unit tests, request logging,
and baseline database index SQL.

## Phase Status

| Phase | Status | Goal | Result | Detail |
| --- | --- | --- | --- | --- |
| Phase 1 | Complete | Build the production core pipeline from the POC workflow. | Folder/note/relation/evidence processing works with PostgreSQL + pgvector and soft delete. | [phase-1.md](phase-1.md) |
| Phase 2 | Complete | Expose the core pipeline through FastAPI. | Protected folder, note, relation, and evidence APIs are available with stable response contracts. | [phase-2.md](phase-2.md) |
| Phase 3 | Complete | Add explanation generation for relations. | Explanation API supports read-only `GET` and get-or-create `POST` using stored `llm_payload`. | [phase-3.md](phase-3.md) |
| Phase 4 | Complete | Prepare internal Ubuntu/nohup deployment. | Server package, readiness checks, nohup scripts, and server smoke tests passed. | [phase-4.md](phase-4.md) |
| Phase 5 | Complete | Improve internal observability, DB performance readiness, and maintainability. | Logging, timing logs, DB index SQL, constants, payload helper, and server verification are complete. | [phase-5.md](phase-5.md) |

## Current Completion Boundary

The current system is ready for internal/private deployment with:

- `127.0.0.1:6550`
- API key authentication
- PostgreSQL + pgvector
- no-sudo `nohup` process management
- manual database SQL setup
- production-safe unit tests and readiness checks

Future work beyond the current boundary includes public exposure, nginx/TLS,
sudo-managed systemd, advanced monitoring, connection pooling, and heavier load
testing.
