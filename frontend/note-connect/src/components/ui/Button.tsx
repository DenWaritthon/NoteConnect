import Link from "next/link";
import type { ComponentPropsWithoutRef, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost";

const variantClassNames: Record<ButtonVariant, string> = {
  primary:
    "border-transparent bg-[var(--color-primary)] text-[var(--color-primary-foreground)] shadow-sm hover:bg-[var(--color-primary-strong)]",
  secondary:
    "border-[var(--color-border)] bg-[var(--color-panel)] text-[var(--color-foreground)] hover:bg-[var(--color-panel-strong)]",
  ghost:
    "border-transparent bg-transparent text-[var(--color-muted-foreground)] hover:bg-[var(--color-panel)] hover:text-[var(--color-foreground)]",
};

const baseClassName =
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border px-4 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)]";

type ButtonProps = ComponentPropsWithoutRef<"button"> & {
  variant?: ButtonVariant;
};

type ButtonLinkProps = ComponentPropsWithoutRef<typeof Link> & {
  children: ReactNode;
  variant?: ButtonVariant;
};

export function Button({
  className = "",
  variant = "primary",
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${baseClassName} ${variantClassNames[variant]} ${className}`}
      {...props}
    />
  );
}

export function ButtonLink({
  className = "",
  variant = "primary",
  ...props
}: ButtonLinkProps) {
  return (
    <Link
      className={`${baseClassName} ${variantClassNames[variant]} ${className}`}
      {...props}
    />
  );
}
