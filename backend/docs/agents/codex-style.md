# Codex Style

This file defines how Codex should behave when helping with code in this repository.

Codex should act like a careful backend teammate, not an automatic code generator.

---

## Work Style

- Make small, reviewable changes.
- Prefer simple code over clever code.
- Do not rewrite unrelated files.
- Do not change existing POC behavior unless explicitly requested.
- Keep existing behavior unchanged unless the task requires a change.
- If a task is ambiguous, make the safest minimal assumption and continue.
- Explain assumptions briefly.

---

## Before Editing Code

Before making changes, Codex should:

1. Read the relevant files.
2. Identify the smallest safe change.
3. Check whether the change affects:
   - AI pipeline
   - database schema
   - API behavior
   - tests
   - POC behavior

For complex changes, create a short plan first.

---

## When Writing Code

- Write complete, usable code.
- Keep imports clean.
- Avoid unused dependencies.
- Prefer clear function names.
- Prefer type hints.
- Keep functions focused on one responsibility.
- Avoid large functions.
- Avoid hidden side effects.
- Do not hardcode database credentials, thresholds, or model paths when they should be configurable.

---

## When Refactoring

- Preserve existing behavior.
- Refactor in small steps.
- Do not combine unrelated refactors.
- Move logic into the correct layer:
  - API layer: request/response only
  - Service layer: business and AI logic
  - Data layer: database access and data structures
  - Core layer: shared config and connection setup
- Keep the POC unchanged unless explicitly requested.

---

## When Working With AI Logic

- Follow `ai-logic.md`.
- Do not bypass the AI pipeline.
- Do not replace pgvector search with manual full-pair comparison.
- Do not expose embeddings through API responses.
- Keep model loading isolated and mockable.
- If NLI is unavailable, use the documented fallback behavior.

---

## When Working With Database Code

- Use `database/er_diagram.dbml` as the schema reference.
- Do not assume Codex can access the PostgreSQL server.
- Update SQL files when schema-related code changes.
- Explain migration impact when schema changes.
- Keep SQL/database access inside the Data layer.

---

## When Working With API

- Follow `api.md`.
- Use FastAPI routers for API endpoints.
- Use Pydantic schemas for request and response validation.
- Use reusable FastAPI dependencies for API key validation.
- Keep API routes focused on request and response handling only.
- Connect API routes to Service layer functions.
- Keep API responses frontend-friendly.
- Do not put business logic in API routes.
- Do not access the database directly from API routes.
- Do not send API keys through query strings.
- Do not hardcode API keys.
- Do not commit real API secrets.
- Do not silently change API behavior without documenting it.