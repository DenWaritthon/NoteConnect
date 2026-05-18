const KEY = "noteconnect_notes";

export const loadNotes = <T,>(): T[] => {
  if (typeof window === "undefined") return [];
  const data = localStorage.getItem(KEY);
  return data ? JSON.parse(data) : [];
};

export const saveNotes = (notes: unknown[]) => {
  localStorage.setItem(KEY, JSON.stringify(notes));
};
