# Repository Guidelines

## Project Structure & Module Organization

This repository contains the Python backend for NoteConnect.

- `main.py` is the intended backend entry point; it is currently empty.
- `src/` is reserved for production modules. Move reusable backend code here as it matures.
- `poc/` contains the current proof-of-concept note relationship workflow, including `NoteStore.py`, `SentenceProcessor.py`, and `main.py`.
- `database/` stores database design and setup files: DBML diagrams plus SQL for extensions, tables, and indexes.
- `requirements.txt` pins Python dependencies for embeddings, NLI, PostgreSQL, and CLI support.

## Build, Test, and Development Commands

Create and activate a local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the current prototype:

```bash
python poc/main.py
```

Apply database setup manually with a PostgreSQL client in this order: `database/create_extension.sql`, `database/create_table.sql`, then `database/create_index.sql`.

## Coding Style & Naming Conventions

Use Python 3.12 style with 4-space indentation, type hints for public functions, and dataclasses for simple data records. Prefer `snake_case` for functions, variables, and module names. Existing proof-of-concept files use some `PascalCase` module names; keep imports consistent there, but use lowercase module names for new production code in `src/`.

Keep comments short and focused on non-obvious logic. Avoid committing generated caches such as `__pycache__/` or local environment files from `.venv/`.

## Testing Guidelines

No automated test suite is present yet. Add tests under `tests/` as production code moves into `src/`. Prefer `pytest`, with files named `test_<module>.py` and tests named `test_<behavior>()`.

For model-heavy code, isolate pure logic such as threshold calculation and relationship classification so it can be tested without downloading transformer models. Run tests with:

```bash
pytest
```

## Commit & Pull Request Guidelines

Git history currently contains a single setup commit, so there is no established convention beyond concise imperative summaries. Use messages such as `Add note relationship classifier` or `Create database indexes`.

Pull requests should include a short description, commands run locally, database migration notes when SQL changes, and screenshots or terminal output only when they clarify behavior. Link related issues when available.

## Security & Configuration Tips

Do not commit credentials, database URLs, model cache contents, or local virtual environments. Keep environment-specific settings in ignored local files and document required variables in the PR or README when adding them.
