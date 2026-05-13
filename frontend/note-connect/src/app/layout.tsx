import type { Metadata } from "next";
import { cookies } from "next/headers";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "NoteConnect",
  description: "A focused note workspace for discovering relationships between ideas.",
};

function getServerTheme(value?: string) {
  return value === "light" || value === "dark" ? value : undefined;
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const serverTheme = getServerTheme(cookieStore.get("note-connect-theme")?.value);

  return (
    <html
      lang="en"
      data-theme={serverTheme}
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <head>
        <Script id="note-connect-theme" strategy="beforeInteractive">
          {`
              try {
                var storedTheme = window.localStorage.getItem("note-connect-theme");
                var theme = storedTheme === "light" || storedTheme === "dark"
                  ? storedTheme
                  : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
                document.documentElement.dataset.theme = theme;
                document.cookie = "note-connect-theme=" + theme + "; path=/; max-age=31536000; SameSite=Lax";
              } catch (_) {}
            `}
        </Script>
      </head>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
