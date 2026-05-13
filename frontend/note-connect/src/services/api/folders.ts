import { apiClient } from "./client";
import type {
  CreateFolderInput,
  DeleteResponse,
  Folder,
  FolderOpenedResponse,
  UpdateFolderInput,
} from "@/types/api";

export function getFolders(options?: { signal?: AbortSignal }) {
  return apiClient.get<Folder[]>("/folders", options);
}

export function createFolder(input: CreateFolderInput) {
  return apiClient.post<Folder>("/folders", input);
}

export function getFolder(folder_id: string, options?: { signal?: AbortSignal }) {
  return apiClient.get<Folder>(`/folders/${encodeURIComponent(folder_id)}`, options);
}

export function updateFolder(folder_id: string, input: UpdateFolderInput) {
  return apiClient.patch<Folder>(
    `/folders/${encodeURIComponent(folder_id)}`,
    input,
  );
}

export function openFolder(folder_id: string) {
  return apiClient.patch<FolderOpenedResponse>(
    `/folders/${encodeURIComponent(folder_id)}/open`,
  );
}

export function deleteFolder(folder_id: string) {
  return apiClient.delete<DeleteResponse>(
    `/folders/${encodeURIComponent(folder_id)}`,
  );
}
