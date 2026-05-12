CREATE TABLE noteconnect_folder (
  folder_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_open_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE noteconnect_note (
  note_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id UUID NOT NULL REFERENCES noteconnect_folder(folder_id) ON DELETE CASCADE,

  sentence TEXT NOT NULL,
  sentence_embedding VECTOR(768),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE noteconnect_note_relation (
  relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id UUID NOT NULL REFERENCES noteconnect_folder(folder_id) ON DELETE CASCADE,

  note_1_id UUID NOT NULL REFERENCES noteconnect_note(note_id) ON DELETE CASCADE,
  note_2_id UUID NOT NULL REFERENCES noteconnect_note(note_id) ON DELETE CASCADE,

  relation_type VARCHAR(50),
  process_status VARCHAR(50) NOT NULL DEFAULT 'relation_confirmed',

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,

  CONSTRAINT chk_note_relation_not_self
    CHECK (note_1_id <> note_2_id),

  CONSTRAINT uq_note_relation_pair
    UNIQUE (folder_id, note_1_id, note_2_id)
);

CREATE TABLE noteconnect_note_relation_evidence (
  evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  relation_id UUID NOT NULL REFERENCES noteconnect_note_relation(relation_id) ON DELETE CASCADE,

  similarity_score DOUBLE PRECISION NOT NULL,
  nli_score JSONB,
  nli_label VARCHAR(50) NOT NULL,

  words_overlap JSONB,
  similar_words JSONB,
  explanation TEXT,
  llm_payload JSONB,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);