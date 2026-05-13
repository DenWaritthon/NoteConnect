import type { ReactNode } from "react";

type StatusStateProps = {
  title: string;
  description: string;
  action?: ReactNode;
};

export function LoadingState({
  title = "Loading",
  description = "Preparing the workspace.",
}: Partial<StatusStateProps>) {
  return (
    <div
      aria-live="polite"
      className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5"
    >
      <div className="mb-4 h-2 w-24 overflow-hidden rounded-full bg-[var(--color-panel-strong)]">
        <div className="h-full w-1/2 animate-pulse rounded-full bg-[var(--color-primary)]" />
      </div>
      <p className="text-sm font-semibold text-[var(--color-foreground)]">
        {title}
      </p>
      <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
        {description}
      </p>
    </div>
  );
}

export function EmptyState({ title, description, action }: StatusStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-panel)] p-5">
      <p className="text-sm font-semibold text-[var(--color-foreground)]">
        {title}
      </p>
      <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
        {description}
      </p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ title, description, action }: StatusStateProps) {
  return (
    <div
      role="alert"
      className="rounded-lg border border-[var(--color-danger-border)] bg-[var(--color-danger-surface)] p-5"
    >
      <p className="text-sm font-semibold text-[var(--color-danger)]">
        {title}
      </p>
      <p className="mt-1 text-sm text-[var(--color-muted-foreground)]">
        {description}
      </p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
