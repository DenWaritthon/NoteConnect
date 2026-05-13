# Backend File Structure

This document explains what each backend folder is for, what is safe to edit,
and which files are references or manual server setup inputs.

## Backend Root

```text
backend/
  main.py
  requirements.txt
  .env.example
  .env
```

| Path | Purpose | Edit Guidance |
| --- | --- | --- |
| `main.py` | FastAPI app factory, lifespan startup, router registration, shared service wiring. | Edit only when changing app-level wiring, middleware, or startup behavior. |
| `requirements.txt` | Python dependencies for local/server runtime. | Edit when dependencies are intentionally added or removed. |
| `.env.example` | Safe reference for required environment variables. | Keep updated when config changes. Do not put secrets here. |
| `.env` | Local/server runtime secrets and settings. | Do not commit. Create manually per environment. |

## Production Source

```text
backend/src/
  api/
  core/
  data/
  services/
```

`backend/src/` is the production backend code. Most feature work should happen
inside this folder.

## API Layer

```text
backend/src/api/
  dependencies.py
  schemas.py
  routers/
    health_router.py
    folder_router.py
    note_router.py
    relation_router.py
```

| File | Purpose | Edit Guidance |
| --- | --- | --- |
| `dependencies.py` | API key validation and shared service dependencies. | Edit when changing auth/dependency wiring. Do not put business logic here. |
| `schemas.py` | Pydantic request and response schemas. | Edit when API contracts change. Do not expose embeddings or raw DB rows. |
| `health_router.py` | Public `GET /health` and `GET /ready`. | Edit for readiness behavior only. |
| `folder_router.py` | Folder endpoints. | Keep route handlers thin; delegate to services. |
| `note_router.py` | Note endpoints. | Do not call AI models or SQL directly here. |
| `relation_router.py` | Relation, evidence, and explanation endpoints. | Keep GET read-only; POST explanation is get-or-create. |

## Core Layer

```text
backend/src/core/
  config.py
  constants.py
  database.py
  logging.py
  model_readiness.py
  timing.py
```

| File | Purpose | Edit Guidance |
| --- | --- | --- |
| `config.py` | Loads `.env` and exposes runtime config. | Add new env settings here and document them in `.env.example`. |
| `constants.py` | Shared status values, payload keys, and common messages. | Use this for repeated domain constants. |
| `database.py` | psycopg3 connection and transaction helpers. | Keep DB connection behavior centralized. |
| `logging.py` | Logging setup and request logging middleware. | Edit when changing observability. |
| `model_readiness.py` | Resolves local model paths and detects missing/Git LFS pointer model files. | Edit when changing offline model readiness checks. |
| `timing.py` | Small timing helper for service logs. | Keep lightweight and dependency-free. |

## Data Layer

```text
backend/src/data/
  evidence_repository.py
  folder_repository.py
  models.py
  note_repository.py
  relation_repository.py
```

| File | Purpose | Edit Guidance |
| --- | --- | --- |
| `models.py` | Dataclasses shared between repositories and services. | Keep aligned with DB rows and API needs. |
| `folder_repository.py` | SQL for folders. | SQL belongs here, not in routers/services. |
| `note_repository.py` | SQL for notes and pgvector similarity search. | Keep similarity search in PostgreSQL. |
| `relation_repository.py` | SQL for relation create/list/status/soft delete. | Keep relation table names aligned with DBML. |
| `evidence_repository.py` | SQL for relation evidence and explanation updates. | Latest active evidence lookup lives here. |

Do not use an ORM unless explicitly requested. Database access should stay in
this layer.

## Service Layer

```text
backend/src/services/
  explanation_generator.py
  explanation_service.py
  folder_service.py
  llm_payload.py
  note_service.py
  relation_query_service.py
  relation_service.py
  sentence_processor.py
```

| File | Purpose | Edit Guidance |
| --- | --- | --- |
| `folder_service.py` | Folder validation, metadata update, open, list, soft delete. | Business rules for folder timestamps live here. |
| `note_service.py` | Note create/update/delete, embedding generation, relation rebuilds. | Main Phase 1 pipeline orchestration. |
| `relation_service.py` | Relation classification rules. | Edit when relation type rules change. |
| `relation_query_service.py` | Read workflows for relation/evidence endpoints. | No recomputation here. |
| `sentence_processor.py` | Embedding, NLI, word overlap, similar words. | AI logic for relation discovery. |
| `llm_payload.py` | Builds the AGENTS.md-compliant explanation payload. | Keep payload shape stable unless requirements change. |
| `explanation_generator.py` | LLM-backed explanation text generator. | Loads/generates explanation text, not DB writes. |
| `explanation_service.py` | Explanation get-or-create workflow and DB updates. | Uses latest active evidence only. |

## Scripts

```text
backend/scripts/
  check_deploy_ready.py
  check_db_ready.py
  check_model_ready.py
  run_server.sh
  start_nohup.sh
  stop_nohup.sh
```

| File | Purpose | When To Run |
| --- | --- | --- |
| `check_deploy_ready.py` | Validates config, imports, packages, and `main:app` availability. | Before starting the service on server. |
| `check_db_ready.py` | Validates PostgreSQL connectivity with current `.env`. | Before starting and after DB/config changes. |
| `check_model_ready.py` | Validates local model files and offline model loading. | Before starting and after model/config changes. |
| `run_server.sh` | Starts uvicorn in foreground using `.env`. | Local/manual server run. |
| `start_nohup.sh` | Starts the API with `nohup`, writes PID/log under `runtime/`. | Internal no-sudo deployment. |
| `stop_nohup.sh` | Stops the process from `runtime/noteconnect.pid`. | Stop/restart deployment. |

Generated runtime files such as `backend/runtime/noteconnect.pid` and
`backend/runtime/noteconnect.log` are server outputs, not source files.

## Local Models

```text
backend/model/
  all-mpnet-base-v2/
  nli-deberta-v3-base/
  Qwen3-0.6B/
```

These directories hold locally cloned AI models for offline/internal runtime.
They are runtime assets, not application source code. Do not edit files inside
them manually, and do not commit large model weights into the application repo.
If a weight file is only a Git LFS pointer, run `git lfs pull` inside that model
directory before starting the API.

## Tests

```text
backend/tests/
  test_api_contract.py
  test_operability.py
  test_repository_contract.py
  test_runtime_config.py
  test_service_pipeline.py
```

| File | Purpose |
| --- | --- |
| `test_api_contract.py` | API shape, auth, response status, and fake-service behavior. |
| `test_operability.py` | Runtime scripts, deploy checks, logging config, index SQL presence. |
| `test_repository_contract.py` | Static checks that repository SQL uses current table names. |
| `test_runtime_config.py` | `.env` config mapping, docs disabling, readiness behavior. |
| `test_service_pipeline.py` | Service rules for relation payloads and explanation workflow. |

These are production-safe fast tests. They do not load AI models or write
application data to PostgreSQL.

## Database Files

```text
backend/database/
  create_extension.sql
  create_table.sql
  create_index.sql
  er_diagram.dbml
```

These files are database setup/reference files. They are not executed by the
application.

| File | Purpose | Server Usage |
| --- | --- | --- |
| `create_extension.sql` | pgvector extension setup reference. | Run manually when preparing a new DB, if needed. |
| `create_table.sql` | Table creation SQL matching the current schema. | Run manually when creating a new DB schema. |
| `create_index.sql` | Performance baseline indexes for active records and pgvector search. | Run manually on the server after tables exist. |
| `er_diagram.dbml` | Source-of-truth schema reference for developers. | Read before changing repository SQL. |

Do not create or modify schema from application code. If database SQL must be
applied, do it manually on the server with the correct DB privileges.

## Documentation

```text
backend/docs/
  agents/
  progrest/
  system-manual/
```

| Folder | Purpose |
| --- | --- |
| `agents/` | Development rules for coding agents and maintainers. |
| `progrest/` | Phase-by-phase progress summaries. |
| `system-manual/` | Human-facing backend manual, including architecture, API, database, deploy, usage, and test details. |

## POC Reference

```text
backend/poc/
```

The POC is reference-only. Do not modify it unless explicitly requested. The
production implementation should copy the useful behavior into `backend/src/`
instead of importing directly from `backend/poc/`.
