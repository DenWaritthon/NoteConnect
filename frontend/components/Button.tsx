"use client";

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary";
};

export default function Button({
  children,
  onClick,
  variant = "primary",
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-4 py-2 rounded-2xl transition shadow-soft",
        variant === "primary"
          ? "bg-primary text-white hover:opacity-90"
          : "bg-white border hover:bg-gray-100"
      )}
    >
      {children}
    </button>
  );
}
