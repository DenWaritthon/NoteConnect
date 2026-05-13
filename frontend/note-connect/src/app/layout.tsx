import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NoteConnect",
  description: "A focused note workspace for discovering relationships between ideas.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <body className="min-h-full">{children}</body>
    </html>
  );
}
