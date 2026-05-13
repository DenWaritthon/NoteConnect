import { AppShell } from "@/components/layout/AppShell";
import { ButtonLink } from "@/components/ui/Button";
import { ApiStatusCard } from "@/features/api-status/ApiStatusCard";

export default function Home() {
  return (
    <AppShell showSidebar={false}>
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
          </div>
        </div>

        <ApiStatusCard />
      </section>
    </AppShell>
  );
}
