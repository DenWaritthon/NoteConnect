"""Interactive Phase 1 terminal demo backed by PostgreSQL.

This mirrors the POC-style workflow while exercising production services and
repositories. It intentionally contains no SQL or AI decision logic.
"""

from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.data.models import FolderRecord
from src.services.folder_service import FolderService
from src.services.note_service import NoteService


DEMO_SENTENCES = [
    "The cat is on the table.",
    "A cat is sitting on the table.",
    "The dog is in the garden.",
    "There is a dog in the garden.",
    "My car is parked outside.",
    "My car is parked in the garage.",
    "The weather is sunny today.",
    "Now is raining outside.",
    "I buy a new umbrella because of the rain.",
    "I love eating pizza.",
]


def print_menu(current_folder: FolderRecord | None) -> None:
    folder_label = (
        f"{current_folder.name} ({current_folder.folder_id})"
        if current_folder is not None
        else "none"
    )
    print(
        "\n"
        f"Current folder: {folder_label}\n"
        "mode:\n"
        "    0  : quit\n"
        "    1  : create folder\n"
        "    2  : list folders\n"
        "    3  : open folder\n"
        "    4  : delete folder\n"
        "    5  : add note to current folder\n"
        "    6  : edit note\n"
        "    7  : delete note\n"
        "    8  : show notes in current folder\n"
        "    9  : show relations in current folder\n"
        "    10 : use demo notes in current folder\n"
    )


def choose_folder(folder_service: FolderService) -> FolderRecord | None:
    folders = folder_service.list_folders()
    if not folders:
        print("No folders found.")
        return None

    print_folders(folders)
    raw_value = input("Enter folder number or folder UUID: ").strip()
    folder_id = resolve_folder_id(raw_value, folders)
    if folder_id is None:
        print("Invalid folder selection.")
        return None

    return folder_service.open_folder(folder_id)


def resolve_folder_id(raw_value: str, folders: list[FolderRecord]) -> UUID | None:
    if raw_value.isdigit():
        index = int(raw_value) - 1
        if 0 <= index < len(folders):
            return folders[index].folder_id
        return None

    try:
        return UUID(raw_value)
    except ValueError:
        return None


def print_folders(folders: list[FolderRecord]) -> None:
    if not folders:
        print("No folders found.")
        return

    print("Folders:")
    for index, folder in enumerate(folders, start=1):
        description = f" - {folder.description}" if folder.description else ""
        print(f"{index}. {folder.name}{description} [{folder.folder_id}]")


def require_current_folder(current_folder: FolderRecord | None) -> FolderRecord | None:
    if current_folder is None:
        print("Open a folder first.")
        return None
    return current_folder


def create_folder(folder_service: FolderService) -> FolderRecord | None:
    name = input("Folder name: ").strip()
    description = input("Description (optional): ").strip()
    try:
        folder = folder_service.create_folder(
            name=name,
            description=description or None,
        )
    except ValueError as error:
        print(error)
        return None

    print(f"Folder created: {folder.name} [{folder.folder_id}]")
    return folder


def delete_folder(
    folder_service: FolderService,
    current_folder: FolderRecord | None,
) -> FolderRecord | None:
    folder = choose_folder(folder_service)
    if folder is None:
        return current_folder

    confirm = input(f"Soft delete folder '{folder.name}'? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return current_folder

    folder_service.delete_folder(folder.folder_id)
    print(f"Folder soft deleted: {folder.name}")

    if current_folder is not None and current_folder.folder_id == folder.folder_id:
        return None
    return current_folder


def add_note(note_service: NoteService, current_folder: FolderRecord) -> None:
    sentence = input("Enter note: ").strip()
    try:
        note = note_service.create_note(
            folder_id=current_folder.folder_id,
            sentence=sentence,
        )
    except ValueError as error:
        print(error)
        return

    print(f"Note saved ID: {note.note_id} - {note.sentence}")


def edit_note(note_service: NoteService, current_folder: FolderRecord) -> None:
    show_notes(note_service, current_folder)
    raw_note_id = input("Enter note UUID to edit: ").strip()
    try:
        note_id = UUID(raw_note_id)
    except ValueError:
        print("Invalid note UUID.")
        return

    sentence = input("Enter new note: ").strip()
    try:
        note = note_service.update_note(
            folder_id=current_folder.folder_id,
            note_id=note_id,
            sentence=sentence,
        )
    except ValueError as error:
        print(error)
        return

    print(f"Note updated ID: {note.note_id} - {note.sentence}")
    print("Related relations and evidence were rebuilt for this note.")


def delete_note(note_service: NoteService, current_folder: FolderRecord) -> None:
    show_notes(note_service, current_folder)
    raw_note_id = input("Enter note UUID to delete: ").strip()
    try:
        note_id = UUID(raw_note_id)
    except ValueError:
        print("Invalid note UUID.")
        return

    confirm = input(f"Soft delete note {note_id}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        note_service.delete_note(
            folder_id=current_folder.folder_id,
            note_id=note_id,
        )
    except ValueError as error:
        print(error)
        return

    print(f"Note soft deleted: {note_id}")


def show_notes(note_service: NoteService, current_folder: FolderRecord) -> None:
    notes = note_service.list_notes(current_folder.folder_id)
    if not notes:
        print("No notes in this folder.")
        return

    print("Notes:")
    for note in notes:
        print(f"- {note.note_id}: {note.sentence}")


def show_relations(note_service: NoteService, current_folder: FolderRecord) -> None:
    relations = note_service.list_relations(current_folder.folder_id)
    if not relations:
        print("No relations in this folder.")
        return

    print("Relations:")
    for relation in relations:
        similarity = (
            f"{relation.similarity_score:.4f}"
            if relation.similarity_score is not None
            else "n/a"
        )
        print(
            f"- {relation.relation_type} | sim={similarity} | "
            f"nli={relation.nli_label or 'n/a'}\n"
            f"  {relation.note_1_id}: {relation.note_1_sentence}\n"
            f"  {relation.note_2_id}: {relation.note_2_sentence}"
        )


def use_demo_notes(note_service: NoteService, current_folder: FolderRecord) -> None:
    for sentence in DEMO_SENTENCES:
        note = note_service.create_note(
            folder_id=current_folder.folder_id,
            sentence=sentence,
        )
        print(f"Demo note saved ID: {note.note_id} - {note.sentence}")


def main() -> None:
    folder_service = FolderService()
    note_service: NoteService | None = None
    current_folder: FolderRecord | None = None

    def get_note_service() -> NoteService:
        """Create NoteService only when note actions need AI models."""
        nonlocal note_service
        if note_service is None:
            note_service = NoteService(config=folder_service.config)
        return note_service

    while True:
        print_menu(current_folder)
        mode = input("Enter mode: ").strip()

        try:
            if mode == "0":
                print("Exiting...")
                break
            if mode == "1":
                created_folder = create_folder(folder_service)
                if created_folder is not None:
                    current_folder = created_folder
            elif mode == "2":
                print_folders(folder_service.list_folders())
            elif mode == "3":
                opened_folder = choose_folder(folder_service)
                if opened_folder is not None:
                    current_folder = opened_folder
                    print(f"Opened folder: {current_folder.name}")
            elif mode == "4":
                current_folder = delete_folder(folder_service, current_folder)
            elif mode == "5":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    add_note(get_note_service(), folder)
            elif mode == "6":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    edit_note(get_note_service(), folder)
            elif mode == "7":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    delete_note(get_note_service(), folder)
            elif mode == "8":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    show_notes(get_note_service(), folder)
            elif mode == "9":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    show_relations(get_note_service(), folder)
            elif mode == "10":
                folder = require_current_folder(current_folder)
                if folder is not None:
                    use_demo_notes(get_note_service(), folder)
            else:
                print("Invalid mode. Please try again.")
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    main()
