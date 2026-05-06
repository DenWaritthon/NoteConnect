"""Note resource endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.api.dependencies import ApiKeyDependency, get_note_service, map_service_error
from src.api.schemas import (
    DeleteResponse,
    NoteCreateRequest,
    NoteResponse,
    NoteUpdateRequest,
)
from src.services.note_service import NoteService


router = APIRouter(
    prefix="/folders/{folder_id}/notes",
    tags=["notes"],
    dependencies=[ApiKeyDependency],
)


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    folder_id: UUID,
    request: NoteCreateRequest,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    try:
        note = service.create_note(
            folder_id=folder_id,
            sentence=request.sentence,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return NoteResponse.from_record(note)


@router.get("", response_model=list[NoteResponse])
def list_notes(
    folder_id: UUID,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> list[NoteResponse]:
    try:
        notes = service.list_notes(folder_id)
    except ValueError as error:
        raise map_service_error(error) from error
    return [NoteResponse.from_record(note) for note in notes]


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    folder_id: UUID,
    note_id: UUID,
    request: NoteUpdateRequest,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    try:
        note = service.update_note(
            folder_id=folder_id,
            note_id=note_id,
            sentence=request.sentence,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return NoteResponse.from_record(note)


@router.delete("/{note_id}", response_model=DeleteResponse)
def delete_note(
    folder_id: UUID,
    note_id: UUID,
    service: Annotated[NoteService, Depends(get_note_service)],
) -> DeleteResponse:
    try:
        service.delete_note(
            folder_id=folder_id,
            note_id=note_id,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return DeleteResponse(deleted=True)
