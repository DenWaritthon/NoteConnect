import { apiClient } from "./client";
import type {
  Relation,
  RelationEvidence,
  RelationExplanation,
} from "@/types/api";

export function getRelations(
  folder_id: string,
  options?: { signal?: AbortSignal },
) {
  return apiClient.get<Relation[]>(
    `/folders/${encodeURIComponent(folder_id)}/relations`,
    options,
  );
}

export function getRelationEvidence(
  folder_id: string,
  relation_id: string,
  options?: { signal?: AbortSignal },
) {
  return apiClient.get<RelationEvidence>(
    `/folders/${encodeURIComponent(folder_id)}/relations/${encodeURIComponent(relation_id)}/evidence`,
    options,
  );
}

export function getRelationExplanation(
  folder_id: string,
  relation_id: string,
  options?: { signal?: AbortSignal },
) {
  return apiClient.get<RelationExplanation>(
    `/folders/${encodeURIComponent(folder_id)}/relations/${encodeURIComponent(relation_id)}/explanation`,
    options,
  );
}

export function generateRelationExplanation(
  folder_id: string,
  relation_id: string,
) {
  return apiClient.post<RelationExplanation>(
    `/folders/${encodeURIComponent(folder_id)}/relations/${encodeURIComponent(relation_id)}/explanation`,
  );
}
