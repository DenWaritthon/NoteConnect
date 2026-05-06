"""Pydantic request and response schemas for the FastAPI layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from src.data.models import (
    FolderRecord,
    NoteRecord,
    RelationEvidenceRecord,
    RelationSummary,
)


class HealthResponse(BaseModel):
    status: str


class DeleteResponse(BaseModel):
    deleted: bool


class FolderCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class FolderResponse(BaseModel):
    folder_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    last_open_at: datetime

    @classmethod
    def from_record(cls, folder: FolderRecord) -> "FolderResponse":
        return cls(
            folder_id=folder.folder_id,
            name=folder.name,
            description=folder.description,
            created_at=folder.created_at,
            updated_at=folder.updated_at,
            last_open_at=folder.last_open_at,
        )


class NoteCreateRequest(BaseModel):
    sentence: str = Field(min_length=1)


class NoteUpdateRequest(BaseModel):
    sentence: str = Field(min_length=1)


class NoteResponse(BaseModel):
    note_id: UUID
    folder_id: UUID
    sentence: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_record(cls, note: NoteRecord) -> "NoteResponse":
        return cls(
            note_id=note.note_id,
            folder_id=note.folder_id,
            sentence=note.sentence,
            created_at=note.created_at,
            updated_at=note.updated_at,
        )


class RelationResponse(BaseModel):
    relation_id: UUID
    folder_id: UUID
    note_1_id: UUID
    note_1_sentence: str
    note_2_id: UUID
    note_2_sentence: str
    relation_type: str
    process_status: str
    similarity_score: float | None
    nli_label: str | None

    @classmethod
    def from_record(cls, relation: RelationSummary) -> "RelationResponse":
        return cls(
            relation_id=relation.relation_id,
            folder_id=relation.folder_id,
            note_1_id=relation.note_1_id,
            note_1_sentence=relation.note_1_sentence,
            note_2_id=relation.note_2_id,
            note_2_sentence=relation.note_2_sentence,
            relation_type=relation.relation_type,
            process_status=relation.process_status,
            similarity_score=relation.similarity_score,
            nli_label=relation.nli_label,
        )


class RelationEvidenceResponse(BaseModel):
    relation_id: UUID
    relation_type: str
    similarity_score: float | None
    nli_label: str | None
    words_overlap: list[str]
    similar_words: list[dict[str, Any]]

    @classmethod
    def from_record(
        cls,
        evidence: RelationEvidenceRecord,
    ) -> "RelationEvidenceResponse":
        return cls(
            relation_id=evidence.relation_id,
            relation_type=evidence.relation_type,
            similarity_score=evidence.similarity_score,
            nli_label=evidence.nli_label,
            words_overlap=evidence.words_overlap,
            similar_words=evidence.similar_words,
        )
