from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from SentenceProcessor import SentenceProcessor


@dataclass
class Note:
    note_id: int
    note: str
    note_vector: np.ndarray


class NoteStore:
    def __init__(self, sentence_processor: SentenceProcessor) -> None:
        self.sentence_processor = sentence_processor
        self.saved_notes: list[Note] = []

    def save_note(self, note_id: int, note: str) -> None:
        """Save a new note, or update an existing note with the same ID."""
        existing_note = self._find_note(note_id)
        note_vector = self.sentence_processor.embedding(note)

        if existing_note is not None:
            existing_note.note = note
            existing_note.note_vector = note_vector
            return

        self.saved_notes.append(
            Note(note_id=note_id, note=note, note_vector=note_vector)
        )

    def update_note(self, note_id: int, note: str) -> bool:
        """Update an existing note. Return True if updated, otherwise False."""
        existing_note = self._find_note(note_id)
        if existing_note is None:
            return False

        existing_note.note = note
        existing_note.note_vector = self.sentence_processor.embedding(note)
        return True

    def delete_note(self, note_id: int) -> bool:
        """Delete an existing note. Return True if deleted, otherwise False."""
        for index, note in enumerate(self.saved_notes):
            if note.note_id == note_id:
                del self.saved_notes[index]
                return True

        return False

    def get_next_note_id(self) -> int:
        if not self.saved_notes:
            return 1
        return max(note.note_id for note in self.saved_notes) + 1

    def get_saved_notes(self) -> list[tuple[int, str]]:
        return [(note.note_id, note.note) for note in self.saved_notes]

    def get_saved_note_by_id(self, note_id: int) -> Optional[str]:
        note = self._find_note(note_id)
        return note.note if note else None

    def has_note(self, note_id: int) -> bool:
        return self._find_note(note_id) is not None

    def get_note_vector(self, note_id: int) -> Optional[np.ndarray]:
        note = self._find_note(note_id)
        return note.note_vector if note else None

    def get_saved_notes_count(self) -> int:
        return len(self.saved_notes)

    def _find_note(self, note_id: int) -> Optional[Note]:
        for note in self.saved_notes:
            if note.note_id == note_id:
                return note
        return None
