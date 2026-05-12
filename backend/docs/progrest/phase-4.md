# Phase 4: Internal/nohup Deploy Readiness

Status: Complete for the current internal/nohup deployment target.

Phase 4 focuses on making the backend ready to deploy on an internal Ubuntu
server without sudo, using `nohup` as the process runner. Public exposure,
nginx/TLS, sudo-managed systemd services, heavy load testing, and advanced
monitoring are outside the current Phase 4 completion boundary.

## Target

- Run API privately on `127.0.0.1:6550`.
- Use `nohup` start/stop scripts because the server has no sudo and no tmux.
- Keep deploy package small: `main.py`, `requirements.txt`, `.env.example`,
  `src/`, `scripts/`, and `tests/`.
- Provide readiness scripts for runtime config and DB connectivity.
- Provide server-safe unit tests that do not write DB rows or load AI models.
- Validate CRUD, relation/evidence, explanation, restart/recovery, auth errors,
  cleanup, logs, and memory behavior on the Ubuntu server.

## Progress

```text
Phase 4 Internal Deploy Planning: 100%
Phase 4 Runtime Scripts:         100%
Phase 4 Server Test Package:     100%
Phase 4 Server Verification:     100%
Phase 4 Documentation:           100%
```

Overall Phase 4 progress:

```text
100%
```

## Completed

- Added production runtime config for host, port, docs toggle, DB readiness, DB
  timeout, log level, and explanation load mode.
- Added FastAPI app factory and `/ready` endpoint.
- Added lazy explanation model loading mode to avoid holding the explanation
  model in RAM between requests.
- Added no-sudo runtime scripts for foreground and `nohup` operation.
- Added deploy readiness checks for runtime config, required packages, imports,
  and database connectivity.
- Added production-server unit tests for API contracts, runtime config,
  service behavior, repository table-name contracts, and deploy scripts.
- Added internal server deploy guide and acceptance checklist.
- Verified deploy package on Ubuntu server:
  - `check_deploy_ready.py` passed.
  - `check_db_ready.py` passed.
  - unit tests passed with `Ran 23 tests OK`.
  - `/health` returned `ok`.
  - `/ready` returned `database: ok`.
  - `nohup` start/stop worked and removed the PID file on stop.
  - folder/note CRUD passed.
  - note creation did not kill the process.
  - relation/evidence creation passed.
  - explanation POST passed.
  - repeated explanation POST returned existing explanation.
  - restart/recovery, auth/bad request, repeated workflow, and cleanup tests
    passed.
  - no important traceback appeared in logs.
  - swap did not increase heavily during the tested workflow.

## Server Memory Observation

```text
Before start:
Mem total 7.8Gi, used 3.7Gi, available 4.0Gi, swap used 3.0Gi

Ready:
Mem total 7.8Gi, used 4.3Gi, available 3.5Gi, swap used 3.0Gi
Process RSS: 943464 KB
```

## Documentation

- [Server Deploy Guide](../system-manual/server-deploy.md)
- [Test Detail](../system-manual/test-detail.md)

## Future Hardening Beyond Phase 4

- Add optional user-level systemd unit files when server policy allows linger or
  a controlled login session.
- Review DB indexes and query plans with larger real data volume.
- Add more detailed latency logging for AI/model workflows.
- Add backup/rollback operational guidance.
- Consider connection pooling if request volume requires it.
- Revisit nginx/TLS only if the API needs to be exposed beyond localhost.
