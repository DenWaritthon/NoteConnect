import { config } from "@/lib/config";
import type { ApiErrorDetail } from "@/types/api";

type HttpMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

type ApiClientOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  timeoutMs?: number;
};

type ApiErrorPayload = {
  detail?: ApiErrorDetail;
  message?: string;
};

export class ApiError extends Error {
  readonly status: number;
  readonly detail: ApiErrorDetail;

  constructor({
    message,
    status,
    detail = null,
  }: {
    message: string;
    status: number;
    detail?: ApiErrorDetail;
  }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

function buildUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  if (typeof window !== "undefined") {
    return `${config.apiProxyBasePath}${normalizedPath}`;
  }

  return new URL(normalizedPath, config.apiBaseUrl).toString();
}

function getErrorMessage(status: number, payload: ApiErrorPayload | null) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  if (typeof payload?.message === "string") {
    return payload.message;
  }

  switch (status) {
    case 400:
      return "The request could not be completed.";
    case 401:
      return "Authentication is required.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "The requested resource was not found.";
    case 422:
      return "Some submitted fields are invalid.";
    case 500:
      return "The API encountered an unexpected error.";
    case 503:
      return "The API is temporarily unavailable.";
    default:
      return `The API returned status ${status}.`;
  }
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();

  if (!text) {
    return undefined as T;
  }

  return JSON.parse(text) as T;
}

async function apiRequest<T>(
  path: string,
  {
    method = "GET",
    body,
    headers = {},
    signal,
    timeoutMs = 5000,
  }: ApiClientOptions = {},
): Promise<T> {
  const requestHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };

  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
  }

  let response: Response;
  const controller = new AbortController();
  const abortRequest = () => {
    controller.abort();
  };
  let timeoutId: ReturnType<typeof globalThis.setTimeout> | undefined;
  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutId = globalThis.setTimeout(() => {
      controller.abort();
      reject(
        new ApiError({
          message: "The API request timed out.",
          status: 0,
          detail: null,
        }),
      );
    }, timeoutMs);
  });

  signal?.addEventListener("abort", abortRequest, { once: true });

  try {
    response = await Promise.race([
      fetch(buildUrl(path), {
        method,
        headers: requestHeaders,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      }),
      timeoutPromise,
    ]);
  } catch (error) {
    if (isApiError(error)) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }

    throw new ApiError({
      message: "Unable to reach the API server.",
      status: 0,
      detail: null,
    });
  } finally {
    if (timeoutId !== undefined) {
      globalThis.clearTimeout(timeoutId);
    }
    signal?.removeEventListener("abort", abortRequest);
  }

  const payload = await parseJsonResponse<unknown>(response).catch(() => null);

  if (!response.ok) {
    const errorPayload =
      payload && typeof payload === "object"
        ? (payload as ApiErrorPayload)
        : null;

    throw new ApiError({
      message: getErrorMessage(response.status, errorPayload),
      status: response.status,
      detail: errorPayload?.detail ?? null,
    });
  }

  return payload as T;
}

export const apiClient = {
  get<T>(path: string, options?: Omit<ApiClientOptions, "method" | "body">) {
    return apiRequest<T>(path, { ...options, method: "GET" });
  },
  post<T>(
    path: string,
    body?: unknown,
    options?: Omit<ApiClientOptions, "method" | "body">,
  ) {
    return apiRequest<T>(path, { ...options, method: "POST", body });
  },
  patch<T>(
    path: string,
    body?: unknown,
    options?: Omit<ApiClientOptions, "method" | "body">,
  ) {
    return apiRequest<T>(path, { ...options, method: "PATCH", body });
  },
  put<T>(
    path: string,
    body?: unknown,
    options?: Omit<ApiClientOptions, "method" | "body">,
  ) {
    return apiRequest<T>(path, { ...options, method: "PUT", body });
  },
  delete<T>(path: string, options?: Omit<ApiClientOptions, "method" | "body">) {
    return apiRequest<T>(path, { ...options, method: "DELETE" });
  },
};
