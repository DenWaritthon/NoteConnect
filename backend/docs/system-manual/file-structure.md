# Backend File Structure

This document describes the production backend file structure.

## Root Backend Files

```text
backend/
  main.py
  requirements.txt
  .env.example
```

- `main.py`: FastAPI entry point. Registers routers and initializes shared services during lifespan startup.
- `requirements.txt`: Python dependencies.
- `.env.example`: reference environment configuration.

## Production Source

```text
backend/src/
  __init__.py
  api/
  core/
  data/
  services/
```

`backend/src/` contains production-ready reusable backend code.

## API Layer

```text
backend/src/api/
  __init__.py
  dependencies.py
  schemas.py
  routers/
    __init__.py
    health_router.py
    folder_router.py
    note_router.py
    relation_router.py
```

- `dependencies.py`: API key validation and shared service dependencies.
- `schemas.py`: Pydantic request and response schemas.
- `health_router.py`: `GET /health`.
- `folder_router.py`: folder endpoints.
- `note_router.py`: note endpoints.
- `relation_router.py`: relation and evidence read endpoints.

## Core Layer

```text
backend/src/core/
  __init__.py
  config.py
  database.py
  logging.py
```

- `config.py`: loads `.env`, database config, model config, API key config, and thresholds.
- `database.py`: creates psycopg connections and transaction context managers.
- `logging.py`: configures process logging for runtime scripts and FastAPI startup.

## Data Layer

```text
backend/src/data/
  __init__.py
  evidence_repository.py
  folder_repository.py
  models.py
  note_repository.py
  relation_repository.py
```

- `models.py`: dataclasses shared between repositories and services.
- `folder_repository.py`: SQL for folder records.
- `note_repository.py`: SQL for notes and pgvector similarity search.
- `relation_repository.py`: SQL for relation create/list/soft delete.
- `evidence_repository.py`: SQL for relation evidence create/detail.

## Service Layer

```text
backend/src/services/
  __init__.py
  explanation_generator.py
  explanation_service.py
  folder_service.py
  note_service.py
  relation_query_service.py
  relation_service.py
  sentence_processor.py
```

- `explanation_generator.py`: LLM-backed relation explanation generator.
- `explanation_service.py`: explanation read/create workflow.
- `folder_service.py`: folder validation, metadata update, open, and soft delete workflows.
- `note_service.py`: note writes, embeddings, relation rebuilds, and note reads.
- `relation_query_service.py`: relation and evidence read workflows for API endpoints.
- `relation_service.py`: relation classification rules.
- `sentence_processor.py`: embedding, NLI, word overlap, and similar word helpers.

## Scripts

```text
backend/scripts/
  check_deploy_ready.py
  check_db_ready.py
  run_server.sh
  start_nohup.sh
  stop_nohup.sh
```

- `check_deploy_ready.py`: verifies production runtime configuration, imports, and required packages.
- `check_db_ready.py`: verifies the configured PostgreSQL database is reachable.
- `run_server.sh`: starts uvicorn with production-safe single-worker settings.
- `start_nohup.sh`: starts the backend in no-sudo `nohup` mode and writes runtime PID/log files.
- `stop_nohup.sh`: stops the `nohup` process from the recorded PID file.

Development-only manual demo and real integration scripts are not part of the
server deploy script set.

## Tests

```text
backend/tests/
  __init__.py
  test_api_contract.py
  test_operability.py
  test_repository_contract.py
  test_runtime_config.py
  test_service_pipeline.py
```

- `test_api_contract.py`: fast API contract tests using FastAPI `TestClient`
  and fake services.
- `test_operability.py`: deploy script, readiness script, and logging checks.
- `test_repository_contract.py`: static checks for production table names in repository SQL.
- `test_runtime_config.py`: production runtime configuration and readiness endpoint checks.
- `test_service_pipeline.py`: service-layer tests for relation evidence payload
  and explanation workflow behavior.

## Database Files

```text
backend/database/
  create_extension.sql
  create_index.sql
  create_table.sql
  er_diagram.dbml
```

These files define and document the PostgreSQL schema and pgvector setup. They
are intended to be applied manually by the developer. `create_index.sql`
contains the current performance baseline indexes for active folders, notes,
relations, latest evidence lookup, and pgvector similarity search.

## Documentation

```text
backend/docs/
  agents/
  progrest/
  system-manual/
```

- `agents/`: coding and architecture rules for AI-assisted development.
- `progrest/`: phase progress summaries.
- `system-manual/`: backend system manual, including API usage, server deploy,
  and test details.

## POC

```text
backend/poc/
```

The POC remains a reference for workflow behavior and should not be modified
unless explicitly requested.
