"use client";

type NoteItemProps = {
  note: {
    title: string;
  };
  active: boolean;
  onClick?: () => void;
};

export default function NoteItem({ note, active, onClick }: NoteItemProps) {
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer rounded-2xl p-4 shadow-soft transition ${
        active ? "bg-primary" : "bg-white hover:bg-gray-100"
      }`}
    >
      <h3 className="truncate font-medium">{note.title}</h3>
    </div>
  );
}
