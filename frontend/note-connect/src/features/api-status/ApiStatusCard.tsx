"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { getReady, isApiError } from "@/services/api";
import type { ReadyResponse } from "@/types/api";

type ApiStatus =
  | { state: "checking" }
  | { state: "ready"; data: ReadyResponse }
  | { state: "error"; message: string; status?: number };

function getStatusMessage(error: unknown) {
  if (isApiError(error)) {
    return {
      message: error.message,
      status: error.status === 0 ? undefined : error.status,
    };
  }

  if (error instanceof Error) {
    return { message: error.message };
  }

  return { message: "Unable to check API readiness." };
}

export function ApiStatusCard() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>({ state: "checking" });

  const handleReadyCheck = useCallback((signal?: AbortSignal) => {
    getReady({ signal })
      .then((data) => {
        setApiStatus({ state: "ready", data });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setApiStatus({ state: "error", ...getStatusMessage(error) });
      });
  }, []);

  const retryStatusCheck = useCallback(() => {
    setApiStatus({ state: "checking" });
    handleReadyCheck();
  }, [handleReadyCheck]);

  useEffect(() => {
    const controller = new AbortController();

    getReady({ signal: controller.signal })
      .then((data) => {
        setApiStatus({ state: "ready", data });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setApiStatus({ state: "error", ...getStatusMessage(error) });
      });

    return () => {
      controller.abort();
    };
  }, []);

  return (
    <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-[var(--color-foreground)]">
            API Status
          </p>
          <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
            Development-only readiness check for local frontend and backend
            integration.
          </p>
        </div>
        <StatusBadge state={apiStatus.state} />
      </div>

      <div className="mt-4 rounded-lg bg-[var(--color-panel-strong)] p-4">
        {apiStatus.state === "checking" ? (
          <p className="text-sm text-[var(--color-muted-foreground)]">
            Checking API readiness...
          </p>
        ) : null}

        {apiStatus.state === "ready" ? (
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-[var(--color-muted-foreground)]">Status</dt>
              <dd className="font-semibold text-[var(--color-foreground)]">
                {apiStatus.data.status}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-[var(--color-muted-foreground)]">Database</dt>
              <dd className="font-semibold text-[var(--color-foreground)]">
                {apiStatus.data.database ?? "not checked"}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-[var(--color-muted-foreground)]">
                Explanation loading
              </dt>
              <dd className="font-semibold text-[var(--color-foreground)]">
                {apiStatus.data.explanation_load_mode ?? "unknown"}
              </dd>
            </div>
          </dl>
        ) : null}

        {apiStatus.state === "error" ? (
          <div>
            <p className="text-sm font-semibold text-[var(--color-danger)]">
              API unavailable
            </p>
            <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
              {apiStatus.message}
              {apiStatus.status ? ` Status ${apiStatus.status}.` : ""}
            </p>
            <Button
              type="button"
              variant="secondary"
              className="mt-4"
              onClick={retryStatusCheck}
            >
              Retry
            </Button>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function StatusBadge({ state }: { state: ApiStatus["state"] }) {
  const label =
    state === "ready" ? "Ready" : state === "error" ? "Offline" : "Checking";
  const className =
    state === "ready"
      ? "bg-[var(--color-primary)] text-[var(--color-primary-foreground)]"
      : state === "error"
        ? "bg-[var(--color-danger-surface)] text-[var(--color-danger)]"
        : "bg-[var(--color-panel-strong)] text-[var(--color-muted-foreground)]";

  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${className}`}>
      {label}
    </span>
  );
}
