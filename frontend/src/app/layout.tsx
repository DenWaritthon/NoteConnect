import "./globals.css";
import Header from "@/components/Header";

export const metadata = {
  title: "NoteConnect",
  description: "Note-taking app built with Next.js",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main className="pt-20">{children}</main>
      </body>
    </html>
  );
}