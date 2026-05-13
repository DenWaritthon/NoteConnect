import Link from "next/link";

const sections = [
  { href: "/folders", label: "Folders", meta: "Organize notes" },
  { href: "/folders/new", label: "New note", meta: "Capture quickly" },
  { href: "/folders/demo/graph", label: "Graph", meta: "Explore links" },
  { href: "/folders/demo/relations", label: "Relations", meta: "Review evidence" },
];

export function AppSidebar() {
  return (
    <aside className="border-b border-[var(--color-border)] bg-[var(--color-sidebar)] lg:min-h-[calc(100vh-4rem)] lg:w-72 lg:border-b-0 lg:border-r">
      <div className="mx-auto flex w-full max-w-7xl gap-2 overflow-x-auto px-4 py-3 sm:px-6 lg:mx-0 lg:block lg:px-4 lg:py-6">
        <p className="hidden px-3 text-xs font-semibold uppercase tracking-wider text-[var(--color-muted-foreground)] lg:block">
          Workspace
        </p>
        <div className="flex gap-2 lg:mt-3 lg:block lg:space-y-2">
          {sections.map((section) => (
            <Link
              key={section.href}
              href={section.href}
              className="block min-w-36 rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-3 transition-colors hover:bg-[var(--color-panel-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)] lg:min-w-0"
            >
              <span className="block text-sm font-semibold text-[var(--color-foreground)]">
                {section.label}
              </span>
              <span className="mt-1 block text-xs text-[var(--color-muted-foreground)]">
                {section.meta}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </aside>
  );
}
