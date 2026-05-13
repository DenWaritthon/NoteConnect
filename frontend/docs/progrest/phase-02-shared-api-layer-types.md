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

## Implementation Completed

- Added shared API/domain types in `src/types/api.ts`.
- Added a shared API client in `src/services/api/client.ts`.
- Centralized API base URL handling through `config.apiBaseUrl`.
- Added a same-origin Next.js backend proxy at `src/app/api/backend/[...path]/route.ts` so browser requests do not fail on backend CORS restrictions.
- Added typed request helpers for `GET`, `POST`, `PATCH`, `PUT`, and `DELETE`.
- Added normalized `ApiError` handling for non-2xx responses, network failures, and unavailable API states.
- Added a request timeout so API status checks and future requests do not stay in an indefinite loading state.
- Added public health/ready services in `src/services/api/health.ts`.
- Added folder services in `src/services/api/folders.ts`.
- Added note services in `src/services/api/notes.ts`.
- Added relation, evidence, and explanation services in `src/services/api/relations.ts`.
- Added `src/services/api/index.ts` as the single export surface for API services.
- Chose to preserve backend `snake_case` response fields in frontend service return values for now.
- Added an `ApiStatusCard` feature that checks `GET /ready` through the shared service layer.

## Result

- The frontend now has a typed service layer ready for Phase 3 folder workflows.
- The home page displays an `API Status` card.
- If the backend is available, the card shows readiness, database, and explanation loading information from `/ready`.
- If the backend is unavailable, the card shows a clear offline/error state and a retry action.
- Browser-side service calls use the same-origin `/api/backend` proxy, while server-side service calls can still use `config.apiBaseUrl` directly.
- The page does not go blank when the API request fails.
- Protected folder, note, relation, and graph workflows are still deferred to later phases.

## Verification

- `npm run lint` passed.
- `npm run build` passed.
- Browser verification at `http://localhost:3000` confirmed that the `API Status` card renders and handles the current backend state.
- With the backend unavailable during verification, the card displayed the offline state and retry action instead of staying blank or crashing.
- With the backend running at `http://127.0.0.1:6550`, `GET /api/backend/ready` returned `200 OK`, and the card displayed `Ready`, `Database ready`, and `Explanation loading lazy`.

## Out of Scope

- Completing every page.
- Complex state management.
- Optimistic updates unless they are clearly necessary.
