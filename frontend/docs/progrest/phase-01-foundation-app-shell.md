# Phase 1: Foundation & App Shell

## Goal

Establish the frontend foundation so the project can grow into a production-ready Next.js application without coupling complex workflows to the backend too early.

## Main Work

- Organize `src/components`, `src/features`, `src/hooks`, `src/lib`, `src/services`, and `src/types`.
- Build the main app shell for navigation and workspace content.
- Define the theme from `public/note-connect.svg`.
- Support light mode and dark mode.
- Create reusable UI states for loading, empty, and error cases.
- Prepare responsive layouts for desktop, tablet, and mobile.
- Add configuration for `NEXT_PUBLIC_API_BASE_URL`.

## Expected Outcomes

- The app has a base layout ready to support all pages.
- The theme and visual direction align with the NoteConnect brand.
- Reusable base components exist for important UI states.
- The file structure is ready for clear separation between pages, features, services, hooks, and types.

## Implementation Completed

- Added the frontend base folders: `src/components`, `src/features`, `src/hooks`, `src/lib`, `src/services`, and `src/types`.
- Added layout components for the application shell, top navigation, sidebar navigation, and theme switching.
- Replaced the default Next.js starter page with a NoteConnect home/workspace preview.
- Added reusable UI components for buttons, loading states, empty states, and error states.
- Added theme tokens in `src/app/globals.css` using the logo-aligned yellow, neutral, panel, border, and dark-mode colors.
- Removed the Google font dependency from the app layout so production builds can run without external font downloads.
- Added `src/lib/config.ts` with `NEXT_PUBLIC_API_BASE_URL` support and a development fallback of `http://127.0.0.1:8000`.
- Added `.env.example` with the local API base URL.
- Updated `.gitignore` so `.env.example` is tracked while real `.env` files remain ignored.
- Updated `progrest-status.md` to mark Phase 1 as complete.

## Result

- Running `npm run dev` shows the NoteConnect shell instead of the default Next.js starter page.
- The page includes the NoteConnect brand, primary navigation, sidebar workspace links, a theme toggle, and a workspace preview.
- The environment preview displays the configured API base URL fallback: `http://127.0.0.1:8000`.
- Light and dark theme tokens are available and the theme toggle updates the document theme.
- Loading, empty, and error state components are available for later phases.

## Verification

- `npm run lint` passed.
- `npm run build` passed.
- Browser verification at `http://localhost:3000` confirmed the page title, main heading, theme toggle, and API fallback render correctly.

## Out of Scope

- Full CRUD workflows.
- Graph visualization.
- AI explanation workflows.
