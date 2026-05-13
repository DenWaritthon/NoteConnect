import { apiClient } from "./client";
import type { HealthResponse, ReadyResponse } from "@/types/api";

export function getHealth(options?: { signal?: AbortSignal }) {
  return apiClient.get<HealthResponse>("/health", options);
}

export function getReady(options?: { signal?: AbortSignal }) {
  return apiClient.get<ReadyResponse>("/ready", options);
}
