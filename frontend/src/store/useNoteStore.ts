import { create } from "zustand";
import { v4 as uuid } from "uuid";
import { loadNotes, saveNotes } from "@/lib/storage";

export type Note = {
  id: string;
  title: string;
  content: string;
  createdAt: number;
};

type State = {
  notes: Note[];
  activeNoteId: string | null;

  addNote: () => void;
  updateNote: (id: string, data: Partial<Note>) => void;
  deleteNote: (id: string) => void;
  setActiveNote: (id: string) => void;
};

export const useNoteStore = create<State>((set, get) => ({
  notes: loadNotes<Note>(),
  activeNoteId: null,

  addNote: () => {
    const newNote: Note = {
      id: uuid(),
      title: "Untitled",
      content: "",
      createdAt: Date.now(),
    };

    const notes = [newNote, ...get().notes];
    saveNotes(notes);

    set({ notes, activeNoteId: newNote.id });
  },

  updateNote: (id, data) => {
    const notes = get().notes.map((n) =>
      n.id === id ? { ...n, ...data } : n
    );

    saveNotes(notes);
    set({ notes });
  },

  deleteNote: (id) => {
    const notes = get().notes.filter((n) => n.id !== id);
    saveNotes(notes);

    set({
      notes,
      activeNoteId: notes[0]?.id || null,
    });
  },

  setActiveNote: (id) => set({ activeNoteId: id }),
}));
