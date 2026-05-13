import type { ReactNode } from "react";
import { AppSidebar } from "./AppSidebar";
import { TopNav } from "./TopNav";

type AppShellProps = {
  children: ReactNode;
  showSidebar?: boolean;
};

export function AppShell({ children, showSidebar = true }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-foreground)]">
      <TopNav />
      <div className="lg:flex">
        {showSidebar ? <AppSidebar /> : null}
        <main className="min-w-0 flex-1">
          <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
