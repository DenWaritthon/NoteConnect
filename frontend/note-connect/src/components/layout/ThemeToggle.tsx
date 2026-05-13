"use client";

import { useEffect } from "react";

type Theme = "light" | "dark";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const storedTheme = window.localStorage.getItem("note-connect-theme");

  if (storedTheme === "light" || storedTheme === "dark") {
    return storedTheme;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function ThemeToggle() {
  useEffect(() => {
    const initialTheme = getInitialTheme();

    document.documentElement.dataset.theme = initialTheme;
  }, []);

  function toggleTheme() {
    const currentTheme =
      document.documentElement.dataset.theme === "dark" ||
      document.documentElement.dataset.theme === "light"
        ? (document.documentElement.dataset.theme as Theme)
        : getInitialTheme();
    const nextTheme = currentTheme === "light" ? "dark" : "light";

    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem("note-connect-theme", nextTheme);
  }

  return (
    <button
      type="button"
      aria-label="Toggle color theme"
      onClick={toggleTheme}
      className="inline-flex min-h-10 items-center justify-center rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] px-3 text-sm font-semibold text-[var(--color-foreground)] transition-colors hover:bg-[var(--color-panel-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)]"
    >
      Theme
    </button>
  );
}
