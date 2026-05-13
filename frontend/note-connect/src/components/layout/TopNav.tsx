import Image from "next/image";
import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/folders", label: "Workspace" },
];

export function TopNav() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--color-border)] bg-[color-mix(in_srgb,var(--color-background)_88%,transparent)] backdrop-blur">
      <nav
        aria-label="Primary navigation"
        className="mx-auto flex min-h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8"
      >
        <Link
          href="/"
          className="flex items-center gap-3 rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--color-ring)]"
        >
          <Image
            src="/note-connect.svg"
            alt=""
            width={36}
            height={36}
            className="h-9 w-9 rounded-lg"
            priority
          />
          <span className="text-base font-semibold text-[var(--color-foreground)]">
            NoteConnect
          </span>
        </Link>
        <div className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-lg px-3 py-2 text-sm font-medium text-[var(--color-muted-foreground)] transition-colors hover:bg-[var(--color-panel)] hover:text-[var(--color-foreground)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)]"
            >
              {item.label}
            </Link>
          ))}
        </div>
        <ThemeToggle />
      </nav>
    </header>
  );
}
