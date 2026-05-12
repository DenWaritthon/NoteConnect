# Phase 4: Internal/nohup Deploy Readiness

Status: Complete for the current internal/nohup deployment target.

## Goal

Prepare the backend to run on an internal Ubuntu server with no sudo, no tmux,
and no public internet exposure requirement. The deployment target was a private
API on `127.0.0.1:6550` using `nohup`.

## What Was Built

- Added production runtime config for host, port, docs toggle, DB readiness,
  DB timeout, log level, and explanation load mode.
- Added `/ready` endpoint for operational readiness checks.
- Added foreground server script.
- Added `nohup` start/stop scripts.
- Added deploy readiness script for config, package imports, and `main:app`.
- Added DB readiness script for PostgreSQL connectivity.
- Added server-safe unit tests that do not load AI models or write DB rows.
- Added support for `EXPLANATION_LOAD_MODE=lazy` to reduce long-lived memory
  use on the server.
- Documented deploy package contents and acceptance checklist.

## Result

Phase 4 made the backend operable as an internal service on the Ubuntu server.

The system can now:

- start and stop through `nohup`
- bind to `127.0.0.1:6550`
- validate runtime readiness before use
- validate database connectivity
- run production-safe tests on the server
- survive restart/recovery checks
- process the core API smoke workflow on the server

## Verification Outcome

Server verification passed:

- `check_deploy_ready.py` passed
- `check_db_ready.py` passed
- unit tests passed at Phase 4 completion
- `/health` returned `ok`
- `/ready` returned `database: ok`
- `nohup` start/stop worked
- folder/note CRUD passed
- relation/evidence creation passed
- explanation POST passed
- repeated explanation POST returned existing explanation
- restart/recovery, auth/bad request, repeated workflow, and cleanup checks
  passed
- process stayed alive during tested AI workflows
- swap did not grow abnormally
- no important traceback appeared in tested logs

## Current Boundary

Phase 4 does not include public nginx/TLS exposure, sudo-managed systemd,
advanced monitoring, connection pooling, or heavy load testing.

## Progress

```text
Overall Phase 4 progress: 100%
```
