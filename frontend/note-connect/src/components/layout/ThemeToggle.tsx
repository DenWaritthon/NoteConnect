"use client";

import { useEffect, useRef } from "react";

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
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const initialTheme = getInitialTheme();

    document.documentElement.dataset.theme = initialTheme;
    buttonRef.current?.setAttribute(
      "aria-pressed",
      String(initialTheme === "dark"),
    );

    const animationFrame = window.requestAnimationFrame(() => {
      document.documentElement.dataset.themeReady = "true";
    });

    return () => {
      window.cancelAnimationFrame(animationFrame);
    };
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
    document.cookie = `note-connect-theme=${nextTheme}; path=/; max-age=31536000; SameSite=Lax`;
    buttonRef.current?.setAttribute(
      "aria-pressed",
      String(nextTheme === "dark"),
    );
  }

  return (
    <button
      ref={buttonRef}
      type="button"
      aria-label="Toggle color theme"
      onClick={toggleTheme}
      className="inline-flex min-h-10 w-32 items-center justify-between gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-panel)] px-3 text-sm font-semibold text-[var(--color-foreground)] transition-colors hover:bg-[var(--color-panel-strong)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)]"
    >
      <span className="w-10 text-left">
        <span className="theme-toggle-label-light">Light</span>
        <span className="theme-toggle-label-dark">Dark</span>
      </span>
      <span className="relative h-6 w-11 shrink-0 overflow-hidden rounded-full bg-[var(--color-panel-strong)]">
        <span className="theme-toggle-thumb absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-[var(--color-primary)]" />
      </span>
    </button>
  );
}
