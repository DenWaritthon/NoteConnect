CREATE INDEX idx_note_folder_active
ON note(folder_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_note_relation_folder_active
ON note_relation(folder_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_note_relation_note_1
ON note_relation(note_1_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_note_relation_note_2
ON note_relation(note_2_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_evidence_relation_active
ON note_relation_evidence(relation_id)
WHERE deleted_at IS NULL;