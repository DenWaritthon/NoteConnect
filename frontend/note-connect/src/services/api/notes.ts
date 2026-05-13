import { apiClient } from "./client";
import type {
  CreateNoteInput,
  DeleteResponse,
  Note,
  UpdateNoteInput,
} from "@/types/api";

export function getNotes(folder_id: string, options?: { signal?: AbortSignal }) {
  return apiClient.get<Note[]>(
    `/folders/${encodeURIComponent(folder_id)}/notes`,
    options,
  );
}

export function createNote(folder_id: string, input: CreateNoteInput) {
  return apiClient.post<Note>(
    `/folders/${encodeURIComponent(folder_id)}/notes`,
    input,
  );
}

export function getNote(
  folder_id: string,
  note_id: string,
  options?: { signal?: AbortSignal },
) {
  return apiClient.get<Note>(
    `/folders/${encodeURIComponent(folder_id)}/notes/${encodeURIComponent(note_id)}`,
    options,
  );
}

export function updateNote(
  folder_id: string,
  note_id: string,
  input: UpdateNoteInput,
) {
  return apiClient.put<Note>(
    `/folders/${encodeURIComponent(folder_id)}/notes/${encodeURIComponent(note_id)}`,
    input,
  );
}

export function deleteNote(folder_id: string, note_id: string) {
  return apiClient.delete<DeleteResponse>(
    `/folders/${encodeURIComponent(folder_id)}/notes/${encodeURIComponent(note_id)}`,
  );
}
