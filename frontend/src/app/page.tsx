"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function Home() {
  const router = useRouter();

  return (
    <main className="relative flex min-h-[calc(100svh-5rem)] flex-col overflow-x-hidden">
      <section className="relative flex min-h-[calc(100svh-5rem)] flex-col items-center justify-center overflow-hidden px-4 py-16 text-center sm:px-6 lg:px-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#F4C430_0%,#F4C430_32%,transparent_33%)] opacity-70 blur-3xl" />

        <motion.div
          className="relative z-10 mx-auto max-w-3xl"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="mb-4 text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            CAPTURE NOTES,
            <br />
            DISCOVER CONNECTIONS
          </h1>

          <p className="mb-6 text-base sm:text-lg">
            Turn your notes into a visual graph of relationships
          </p>

          <button
            onClick={() => router.push("/notes")}
            className="rounded-2xl bg-white px-6 py-3 shadow-soft transition hover:scale-105"
          >
            Open Note -&gt;
          </button>
        </motion.div>
      </section>

      <section className="bg-gray-50 px-6 py-16 text-center sm:py-20">
        <div className="mx-auto max-w-3xl space-y-6">
          <h2 className="text-2xl font-semibold sm:text-3xl">
            What is NoteConnect?
          </h2>

          <p className="text-sm leading-7 text-gray-600 sm:text-base">
            NoteConnect is more than just a note-taking app. It helps you capture
            ideas quickly, organize them effortlessly, and most importantly,
            discover how your thoughts connect. Instead of isolated notes, you
            build a network of ideas.
          </p>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 sm:py-20">
        <div className="mx-auto grid max-w-5xl gap-4 sm:grid-cols-2 sm:gap-6 md:grid-cols-3">
          <motion.div
            whileHover={{ y: -6 }}
            className="rounded-2xl bg-white p-6 shadow-soft"
          >
            <h3 className="mb-2 font-semibold">Simple Note Editor</h3>
            <p className="text-sm leading-6 text-gray-500">
              Clean, fast, and distraction-free writing experience like iOS
              Notes.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -6 }}
            className="rounded-2xl bg-white p-6 shadow-soft"
          >
            <h3 className="mb-2 font-semibold">Auto Save</h3>
            <p className="text-sm leading-6 text-gray-500">
              Your notes are saved instantly so you never lose ideas.
            </p>
          </motion.div>

          <motion.div
            whileHover={{ y: -6 }}
            className="rounded-2xl bg-white p-6 shadow-soft sm:col-span-2 md:col-span-1"
          >
            <h3 className="mb-2 font-semibold">Graph Connections</h3>
            <p className="text-sm leading-6 text-gray-500">
              Visualize how your notes relate through an interactive graph.
            </p>
          </motion.div>
        </div>
      </section>

      <footer className="mt-auto border-t px-6 py-10 text-gray-500">
        <div className="mx-auto flex max-w-6xl flex-col justify-between gap-10 md:flex-row">
          <div className="text-left">
            <h2 className="mb-2 font-semibold text-gray-800">NoteConnect</h2>

            <h3 className="mb-2 text-sm font-normal text-gray-800">
              Demo project for FRA502 SPECIAL TOPIC III : WEB PROGRAMMING
            </h3>

            <p className="mb-4 text-sm">Turn your notes into connected ideas.</p>

            <div className="flex gap-6 text-sm">
              <button onClick={() => router.push("/")}>Home</button>
              <button onClick={() => router.push("/notes")}>Notes</button>
            </div>

            <p className="mt-4 text-xs">
              Copyright {new Date().getFullYear()} NoteConnect. All rights
              reserved.
            </p>
          </div>

          <div className="text-left md:text-right">
            <p className="mb-3 font-medium text-gray-800">Developer Team</p>

            <div className="space-y-1 text-xs">
              <p>Chawaphon Wachiraniramit - 65340500014</p>
              <p>Waritthon Kongnoo - 65340500050</p>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
