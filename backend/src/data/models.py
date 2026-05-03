"""Typed records shared between repositories and services.

Repositories map database rows into these dataclasses so higher layers never
need to work with raw cursors or row dictionaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class FolderRecord:
    folder_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    last_open_at: datetime


@dataclass(frozen=True)
class NoteRecord:
    note_id: UUID
    folder_id: UUID
    sentence: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SimilarNote:
    note_id: UUID
    folder_id: UUID
    sentence: str
    similarity_score: float


@dataclass(frozen=True)
class RelationRecord:
    relation_id: UUID
    folder_id: UUID
    note_1_id: UUID
    note_2_id: UUID
    relation_type: str
    process_status: str


@dataclass(frozen=True)
class RelationSummary:
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


@dataclass(frozen=True)
class RelationEvidenceInput:
    relation_id: UUID
    similarity_score: float
    nli_score: dict[str, float]
    nli_label: str
    words_overlap: list[str]
    similar_words: list[dict[str, Any]]
    explanation: str | None = None
    llm_payload: dict[str, Any] | None = None
