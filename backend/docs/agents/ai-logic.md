# AI Logic Overview

This file describes how AI is used in the NoteConnect backend.

The AI system is responsible for:

- converting notes into embeddings
- finding similar notes using pgvector
- validating relationships using NLI
- generating structured relationships between notes
- optionally generating explanation (evidence)

All AI-related logic must be implemented in the Service layer.

---

## Full AI Pipeline

When a note is created or updated, the system runs the following pipeline:

```text
[1] Encode → Embedding
        ↓
[2] Compute Similarity (Top-K search using pgvector)
        ↓
[3] Filter by base similarity threshold
        sim >= base_threshold ?
        ↓
        no → reject
        yes → proceed to NLI
        ↓
[4] NLI
        ↓
        ├── entailment → related_entailment
        ├── contradiction → related_conflict
        └── neutral → candidate_for_similarity_check
                ↓
[5] Strict Similarity Check (for neutral only)
        sim >= updated_threshold ?
                ↓
                yes → related_semantic
                no → reject
                ↓
[6] Generate relation data
        ├── relation_type
        ├── similarity_score
        ├── word overlap
        └── concept overlap
        ↓
[7] Store relation and evidence in database
```
The workflow is based on `poc/`, but similarity computation must use pgvector Top-K search instead of in-memory comparison.

## Relation Type Definition

Relation types describe how the system interprets a note pair after AI validation.

- `related_entailment`
  - The pair is confirmed by NLI entailment.
  - This is a type of relationship that is described as cause and effect.
  
- `related_conflict`
  - The pair is identified as contradiction by NLI.
  - This is a type of relationship that can be described as contradictory.
  
- `related_semantic`
  - The pair is neutral by NLI, but still semantically similar based on a stricter similarity threshold.
  - This means the notes are related by topic or concept, but not directly entailing each other.