from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import UUID


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.services.note_service import NoteService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Phase 1 NoteService demo.")
    parser.add_argument("--folder-id", required=True, type=UUID)
    parser.add_argument("sentences", nargs="+")
    args = parser.parse_args()

    service = NoteService()
    for sentence in args.sentences:
        note = service.create_note(folder_id=args.folder_id, sentence=sentence)
        print(f"Created note {note.note_id}: {note.sentence}")


if __name__ == "__main__":
    main()
