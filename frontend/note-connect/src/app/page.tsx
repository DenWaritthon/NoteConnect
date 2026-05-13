import { AppShell } from "@/components/layout/AppShell";
import { ButtonLink } from "@/components/ui/Button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/ui/StatusState";
import { config } from "@/lib/config";

export default function Home() {
  return (
    <AppShell>
      <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem] lg:items-start">
        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-6 shadow-sm sm:p-8 lg:p-10">
          <p className="text-sm font-semibold uppercase tracking-wider text-[var(--color-muted-foreground)]">
            Smart note workspace
          </p>
          <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-tight text-[var(--color-foreground)] sm:text-5xl">
            Capture notes and uncover the relationships between ideas.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--color-muted-foreground)] sm:text-lg">
            NoteConnect is being shaped into a focused workspace for notes,
            relationship discovery, and graph-based exploration.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <ButtonLink href="/folders">Open Workspace</ButtonLink>
            <ButtonLink href="/folders/demo/graph" variant="secondary">
              Preview Graph
            </ButtonLink>
          </div>
        </div>

        <div className="grid gap-4">
          <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5">
            <p className="text-sm font-semibold text-[var(--color-foreground)]">
              Environment
            </p>
            <p className="mt-2 break-all rounded-lg bg-[var(--color-panel-strong)] px-3 py-2 font-mono text-xs text-[var(--color-muted-foreground)]">
              {config.apiBaseUrl}
            </p>
          </div>
          <LoadingState
            title="Workspace shell ready"
            description="Phase 1 prepares shared states before backend data is connected."
          />
        </div>
      </section>

      <section className="mt-6 grid gap-4 lg:grid-cols-3">
        <EmptyState
          title="No folder selected"
          description="Folder data will be loaded through the shared API layer in the next phase."
          action={<ButtonLink href="/folders">Go to folders</ButtonLink>}
        />
        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5">
          <p className="text-sm font-semibold text-[var(--color-foreground)]">
            Graph surface
          </p>
          <div className="mt-5 aspect-[4/3] rounded-lg border border-[var(--color-border)] bg-[var(--color-panel-strong)] p-4">
            <div className="relative h-full">
              <div className="absolute left-[12%] top-[20%] h-5 w-5 rounded-full bg-[var(--color-primary)] shadow-sm" />
              <div className="absolute left-[48%] top-[42%] h-6 w-6 rounded-full bg-[var(--color-foreground)] shadow-sm" />
              <div className="absolute right-[16%] top-[18%] h-4 w-4 rounded-full bg-[var(--color-muted-foreground)] shadow-sm" />
              <div className="absolute bottom-[18%] left-[28%] h-4 w-4 rounded-full bg-[var(--color-muted-foreground)] shadow-sm" />
              <div className="absolute left-[18%] top-[29%] h-px w-[42%] rotate-12 bg-[var(--color-border)]" />
              <div className="absolute right-[21%] top-[31%] h-px w-[34%] -rotate-12 bg-[var(--color-border)]" />
              <div className="absolute bottom-[34%] left-[33%] h-px w-[27%] rotate-45 bg-[var(--color-border)]" />
            </div>
          </div>
        </div>
        <ErrorState
          title="API not connected yet"
          description="Phase 1 only prepares configuration and UI states. API services arrive in Phase 2."
          action={
            <ButtonLink href="/settings" variant="secondary">
              Open settings
            </ButtonLink>
          }
        />
      </section>
    </AppShell>
  );
}
