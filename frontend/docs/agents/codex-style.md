# Codex Style

Codex should act like a careful frontend production engineer working on a production Next.js application.

---

## Work Style

- Make small, reviewable changes.
- Prefer simple code over clever code.
- Do not rewrite unrelated files.
- Preserve existing frontend behavior unless explicitly requested.
- If a task is ambiguous, make the safest minimal assumption and continue.
- Explain assumptions briefly.

---

## Before Editing Code

Before making changes, Codex should:

1. Read the relevant files.
2. Identify the smallest safe change.
3. Check impact on:
   - routing
   - API integration
   - shared components
   - state management
   - responsiveness
   - accessibility
   - tests

For complex changes, create a short plan first.

---

## When Writing Code

- Write complete, production-usable frontend code.
- Keep imports clean.
- Avoid unused dependencies.
- Prefer clear component and function names.
- Use TypeScript types explicitly.
- Keep components focused on one responsibility.
- Avoid very large components.
- Avoid hidden side effects.
- Prefer reusable UI patterns.
- Keep API logic centralized.
- Avoid hardcoding API URLs, tokens, or environment-specific values.

---

## When Refactoring

- Preserve existing behavior.
- Refactor in small steps.
- Do not combine unrelated refactors.
- Keep logic in the correct layer:
  - Page → workflow composition
  - Feature → domain interaction logic
  - Component → reusable UI
  - Service → API communication
  - Hook → reusable state logic
  - Shared/Core → utilities and configuration

---

## When Working With Frontend State

- Keep server state separate from local UI state.
- Avoid unnecessary global state.
- Keep loading and error handling predictable.
- Avoid duplicated API requests when possible.
- Prefer reusable hooks for shared stateful logic.
- Keep optimistic UI updates safe and reversible.
- Preserve UX consistency across pages.

---

## When Working With API

- Follow `api-detail.md`.
- Use the shared Service/API layer.
- Use typed request/response models.
- Do not duplicate backend business logic.
- Do not hardcode API URLs or secrets.

---

## Security and Repository Rules

- Never commit secrets, API keys, tokens, credentials, or private environment values.
- Never hardcode secrets in frontend code.
- Never upload `.env` files or secret configuration to Git or cloud storage.
- Avoid exposing sensitive values in browser bundles, logs, screenshots, or test fixtures.
- Exclude build artifacts, cache files, temporary files, and generated runtime data from Git.
- Do not commit framework cache directories such as:
  - `.next/`
  - `node_modules/`
  - `.turbo/`
  - cache or temporary build folders
- Do not upload local development databases, logs, or generated AI artifacts unless explicitly required.
- Verify `.gitignore` rules before adding new tooling or generated files.

## Testing Expectations

- Update tests when frontend behavior changes.
- Prefer testing user-visible behavior.
- Keep tests maintainable and resilient.
- Avoid fragile implementation-detail tests.