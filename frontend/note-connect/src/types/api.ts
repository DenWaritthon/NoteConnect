export type ApiErrorDetail =
  | string
  | Array<{
      loc?: Array<string | number>;
      msg?: string;
      type?: string;
    }>
  | Record<string, unknown>
  | null;

export type HealthResponse = {
  status: "ok" | string;
};

export type ReadyResponse = {
  status: "ready" | string;
  database?: "ok" | string;
  explanation_load_mode?: string;
};

export type Folder = {
  folder_id: string;
  name: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string;
  last_open_at?: string | null;
};

export type CreateFolderInput = {
  name: string;
  description?: string | null;
};

export type UpdateFolderInput = {
  name?: string;
  description?: string | null;
};

export type FolderOpenedResponse = {
  folder_id: string;
  last_open_at: string;
};

export type Note = {
  note_id: string;
  folder_id?: string;
  sentence: string;
  created_at?: string;
  updated_at?: string;
};

export type CreateNoteInput = {
  sentence: string;
};

export type UpdateNoteInput = {
  sentence: string;
};

export type Relation = {
  relation_id: string;
  note_1_id: string;
  note_1_sentence: string;
  note_2_id: string;
  note_2_sentence: string;
};

export type RelationEvidence = {
  relation_id: string;
  relation_type: string;
  similarity_score: number;
  nli_label?: string;
  words_overlap?: string[];
  similar_words?: Array<{
    word1: string;
    word2: string;
    score: number;
  }>;
};

export type RelationExplanation = {
  relation_id: string;
  explanation: string;
};

export type DeleteResponse = {
  deleted: boolean;
};
