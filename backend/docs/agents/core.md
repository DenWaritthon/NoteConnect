# Core Instructions

You are a coding assistant for the NoteConnect backend.

Help write, refactor, debug, and organize Python backend code for an AI note relationship system.

## Tech Stack

- Backend: Python
- API: FastAPI
- Database: PostgreSQL + pgvector
- Embedding: Sentence Transformers model `sentence-transformers/all-mpnet-base-v2`
- NLI: Cross Encoder model `cross-encoder/nli-deberta-v3-base`
- LLM for generate explanation: Huggingface model `Qwen/Qwen3-0.6B`

## Project Context

- `poc/` contains the current proof-of-concept workflow.
- `src/` is for production-ready reusable backend code.
- `main.py` is the intended backend entry point.
- `scripts/` is used for code used to test the basic functionality of the system.
- `database/` stores SQL files for PostgreSQL database server setup. The coding agent cannot access the database server directly; these SQL files are intended to be applied manually by the developer.
- `model/` stores the local models that are cloned from hugging face using git.
- `database/er_diagram.dbml` contains the database ER diagram and can be used as a reference when working with database-related code.
- `requirements.txt` manages Python dependencies.
- `.env` 

A POC (Proof of Concept) provides a sample of the entire system's working structure without using APIs or a database. The POC should not be modified unless explicitly requested.It is primarily used as a reference for workflow procedures.

### Environment Variables (.env)

The project uses a `.env` file to store environment-specific configuration.

Examples of configuration:

- database connection settings
- API configuration
- model configuration (if needed)
- threshold values for similarity or NLI

Rules:

- Do not hardcode configuration values in the source code.
- Read configuration from environment variables.
- Assume `.env` exists in the local development environment.
- Do not commit `.env` to version control.
- If new configuration is required, clearly document the variable name and purpose.

## Target Backend Structure

Production code should be organized by responsibility.

Use these layers:

- API layer: receives requests and returns responses.
- Service layer: contains business logic and coordinates the pipeline.
- Data layer: handles database access and defines data structures.
- Core layer: contains shared configuration and database connection setup.

---

### Data Layer Responsibilities

The Data layer is responsible for:

- running SQL queries
- interacting with PostgreSQL
- defining data structures for database records
- mapping database rows to Python objects


## Main Pipeline

When implementing note create/update:

1. Validate input
2. Save/update note
3. Generate embedding
4. Search Top-K similar notes using pgvector
5. Filter results by similarity threshold
6. Validate relation with NLI if available
7. Create relation (with similarity_score and relation_type)
8. Store results

When implementing note delete:

1. Validate input
2. Delete note in database
3. Delete all relations related to the note

When generate explanations of relation:

1. Validate input
2. Load llm_payload from database
3. Generate explanation
4. Store results

## Coding Rules

- Use Python 3.12 style.
- Use type hints.
- Avoid over-engineering.
  
### Naming Conventions

- Use `camel_case` for file names.
- Use `PascalCase` for class names.
- Use `snake_case` for functions, variables, and other identifiers.

### Architecture Rules

- Do not put business logic in API routes.
- Do not access the database outside the Data layer.
- Do not put AI model logic in API routes.
- Keep database access in the Data layer.
- Keep each module focused on one responsibility.

### Safety Rules

- Do not rewrite large parts of the code unless requested.
- Prefer small, incremental changes.
- Keep existing behavior unchanged unless explicitly asked to modify it.