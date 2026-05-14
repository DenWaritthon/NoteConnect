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
            className={`p-4 rounded-2xl transition cursor-pointer shadow-soft ${active
                    ? "bg-primary"
                    : "bg-white hover:bg-gray-100"
                }`}
        >
            <h3 className="font-medium truncate">{note.title}</h3>
        </div>
    );
}
