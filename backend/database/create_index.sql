CREATE INDEX IF NOT EXISTS idx_noteconnect_folder_active_open
ON noteconnect_folder (last_open_at DESC, created_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_note_active_folder_created
ON noteconnect_note (folder_id, created_at)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_note_active_embedding_hnsw
ON noteconnect_note
USING hnsw (sentence_embedding vector_cosine_ops)
WHERE deleted_at IS NULL
  AND sentence_embedding IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_relation_active_folder_created
ON noteconnect_note_relation (folder_id, created_at)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_relation_active_note1
ON noteconnect_note_relation (folder_id, note_1_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_relation_active_note2
ON noteconnect_note_relation (folder_id, note_2_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_noteconnect_evidence_active_relation_created
ON noteconnect_note_relation_evidence (relation_id, created_at DESC)
WHERE deleted_at IS NULL;
