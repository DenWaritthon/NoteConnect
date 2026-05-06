"""Relation resource endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import (
    ApiKeyDependency,
    get_relation_query_service,
    map_service_error,
)
from src.api.schemas import RelationEvidenceResponse, RelationResponse
from src.services.relation_query_service import RelationQueryService


router = APIRouter(
    prefix="/folders/{folder_id}/relations",
    tags=["relations"],
    dependencies=[ApiKeyDependency],
)


@router.get("", response_model=list[RelationResponse])
def list_relations(
    folder_id: UUID,
    service: Annotated[
        RelationQueryService,
        Depends(get_relation_query_service),
    ],
) -> list[RelationResponse]:
    try:
        relations = service.list_relations(folder_id)
    except ValueError as error:
        raise map_service_error(error) from error
    return [RelationResponse.from_record(relation) for relation in relations]


@router.get("/{relation_id}/evidence", response_model=RelationEvidenceResponse)
def get_relation_evidence(
    folder_id: UUID,
    relation_id: UUID,
    service: Annotated[
        RelationQueryService,
        Depends(get_relation_query_service),
    ],
) -> RelationEvidenceResponse:
    try:
        evidence = service.get_relation_evidence(
            folder_id=folder_id,
            relation_id=relation_id,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return RelationEvidenceResponse.from_record(evidence)
