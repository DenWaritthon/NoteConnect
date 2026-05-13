# Phase 2: Shared API Layer & Types

## Goal

Make the frontend a clean, safe, and maintainable API client before building the main workflows.

## Main Work

- Create a shared `apiClient`.
- Read the API base URL from environment variables.
- Centralize authentication and header handling.
- Normalize API errors into a shared format.
- Create shared domain/API types for folders, notes, relations, evidence, and explanations.
- Create services for folders, notes, relations, and health/ready checks.
- Choose a consistent field naming strategy: preserve API `snake_case` or map to `camelCase`.
- Avoid raw `fetch` calls in pages and components.

## Expected Outcomes

- All API calls go through the service layer.
- Pages and features consume typed service functions.
- Errors, unauthorized responses, and network failures are handled centrally.
- Backend contracts are clearly separated from UI components.

## Out of Scope

- Completing every page.
- Complex state management.
- Optimistic updates unless they are clearly necessary.
