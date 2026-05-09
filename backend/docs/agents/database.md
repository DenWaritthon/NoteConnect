# Database Rules

This file defines how Codex should interact with the database in this project.

The database is PostgreSQL with the pgvector extension enabled.

The database is already created and must be used as-is.

---

## Database Access

The backend must access the database using:

- psycopg3 (Python PostgreSQL driver)

Rules:

- All database operations must use psycopg3.
- Do not use other database libraries.
- Do not implement ORM unless explicitly requested.

---

## Configuration

Database connection information is stored in the `.env` file.

Rules:

- Do not hardcode database credentials.
- Read connection settings from environment variables.
- Assume `.env` is already configured.
- Use a central config module to access environment variables.

---

## Database Schema Source

The database schema is already defined and created by the developer.

Schema files are located in:

```text
database/
```

Important files:

- `database/er_diagram.dbml`
- `database/create_table.sql`
- `database/create_index.sql`

Rules:

- Use these files as the source of truth.
- Do not modify schema unless explicitly requested.
- Do not generate new schema.
- Do not assume missing tables or columns.
- Use the existing database structure only.

---

## pgvector Usage

The database uses `pgvector` to store note embeddings and perform similarity search.

Rules:

- Store note embeddings in the existing vector column defined in the database schema.
- The embedding vector must match the dimension defined in the schema.
- For production, the expected embedding dimension is 768 because the project uses `sentence-transformers/all-mpnet-base-v2`.
- Embeddings may be passed from Python as a list or array.
- Embeddings must be stored in PostgreSQL as a pgvector column.
- Do not store embeddings as plain text or JSON.
- Do not calculate similarity manually in Python for production code.
- Use pgvector similarity operators in SQL.

---

## Saving Embeddings

When saving a note embedding:

- Generate the embedding in the Service layer.
- Pass the vector to the Data layer.
- Save the vector using psycopg3.
- Keep database access inside the Data layer.

Example:

```python
cursor.execute(
    """
    UPDATE note
    SET sentence_embedding = %s
    WHERE note_id = %s
    """,
    (embedding, note_id),
)
```

The actual table and column names must follow the existing schema in `database/`.

---

## Similarity Search

Similarity search must be performed using pgvector in PostgreSQL.

Rules:

- Use Top-K search.
- Filter by `folder_id`.
- Exclude the source note.
- Ignore notes where the embedding is NULL.
- Return `similarity_score`.
- Apply threshold filtering when required.
- Do not compare notes across different folders.

pgvector operator:

```text
<=>  cosine distance
```

Similarity formula:

```text
similarity_score = 1 - cosine_distance
```

Higher `similarity_score` means notes are more similar.

Example query:

```sql
SELECT
    note_id,
    sentence,
    1 - (sentence_embedding <=> %(query_embedding)s) AS similarity_score
FROM note
WHERE folder_id = %(folder_id)s
  AND note_id != %(source_note_id)s
  AND sentence_embedding IS NOT NULL
ORDER BY sentence_embedding <=> %(query_embedding)s
LIMIT %(top_k)s;
```

Threshold filtering example:

```sql
SELECT *
FROM (
    SELECT
        note_id,
        sentence,
        1 - (sentence_embedding <=> %(query_embedding)s) AS similarity_score
    FROM note
    WHERE folder_id = %(folder_id)s
      AND note_id != %(source_note_id)s
      AND sentence_embedding IS NOT NULL
    ORDER BY sentence_embedding <=> %(query_embedding)s
    LIMIT %(top_k)s
) AS candidates
WHERE similarity_score >= %(threshold)s;
```

---

## Index Usage

pgvector index should exist on the embedding column for production similarity search.

Rules:

- Do not create indexes in application code.
- Assume indexes are created through SQL files in `database/`.
- Use query patterns that can benefit from pgvector indexes.
- Do not redesign index strategy unless explicitly requested.

---

## Allowed Operations

Codex is allowed to:

- write SELECT, INSERT, UPDATE, and DELETE queries
- read data from existing tables
- save note embeddings
- perform pgvector similarity search
- map query results into Python data structures
- implement Data layer functions using psycopg3

---

## Forbidden Operations

Codex must NOT:

- create or modify database schema
- create new tables or columns
- modify SQL files in `database/`
- apply migrations
- create indexes from application code
- suggest schema redesign unless explicitly asked
- assume database state without checking schema files

---

## Data Layer Rules

All database access must be implemented in the Data layer.

Rules:

- Do not write SQL in API routes.
- Do not write SQL in Service layer.
- Keep query logic isolated in the Data layer.
- Return clean Python data structures, not raw DB cursors.
- Keep database code focused only on database operations.

---

## Query Rules

When writing queries:

- Use parameterized queries.
- Do not use string formatting for SQL values.
- Do not fetch unnecessary columns.
- Keep SQL readable.
- Always filter by `folder_id` when working with folder-specific notes.
- Always use the existing table and column names from the schema files.

---

## Transaction Rules

Use transactions when performing multiple related operations.

Examples:

- create note + save embedding + create relations
- update note + update embedding + rebuild relations
- delete note + delete related relations

Rules:

- Group related operations in a single transaction.
- Roll back the transaction if any step fails.
- Do not leave partial relation or evidence data.

---

## Relation Rules

Each relation should follow the existing `note_relation` table structure:

```text
relation_id
folder_id
note_1_id
note_2_id
relation_type
process_status
created_at
updated_at
deleted_at
```

Allowed `relation_type` values:

```text
related_entailment
related_semantic
related_conflict
```

Allowed `process_status` values:

```text
relation_confirmed
add_explanation
```

Rules:

- Store note pair IDs using `note_1_id` and `note_2_id`.
- Store the related `folder_id` with every relation.
- Do not create duplicate relations for the same note pair in the same folder.
- Keep relation direction consistent.
- Do not store `similarity_score` directly in `note_relation`; it belongs in `note_relation_evidence`.
- Delete or rebuild old relations when a note is updated.
- Delete all relations related to a note when the note is deleted.

---

## Evidence Rules

Evidence should follow the existing `note_relation_evidence` table structure:

```text
evidence_id
relation_id
similarity_score
nli_score
nli_label
words_overlap
similar_words
explanation
llm_payload
created_at
updated_at
deleted_at
```

Rules:

- Store `similarity_score` in `note_relation_evidence`.
- Store raw NLI model scores in `nli_score` as JSONB.
- Store the selected NLI label in `nli_label`.
- Store word overlap data in `words_overlap` as JSONB.
- Store similar word data in `similar_words` as JSONB.
- Store optional explanation text in `explanation`.
- Store optional model/debug payload in `llm_payload` as JSONB.

Example `nli_score`:

```json
{
  "entailment": 0.82,
  "neutral": 0.15,
  "contradiction": 0.03
}
```

Example `llm_payload`:

```json
{
  "note_1": "A cat is sitting on the table.",
  "note_2": "The cat is on the table.",
  "similarity_score": 0.9044219255447388,
  "nli_label": "entailment",
  "words_overlap": ["cat", "table"],
  "similar_words": [{'word1': 'raining', 
                    'word2': 'rain', 
                    'score': 0.8997476100921631}]
}
```
---

## Security Rules

- Do not expose raw embeddings through API responses.
- Do not hardcode database credentials.
- Do not commit `.env`.
- Use environment variables for database configuration.

---

## Final Constraint

The database already exists and must be used as-is.

Codex must focus only on using the database, not redesigning, migrating, or managing it.