"""Folder resource endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import (
    ApiKeyDependency,
    get_folder_service,
    map_service_error,
)
from src.api.schemas import (
    DeleteResponse,
    FolderCreateRequest,
    FolderCreateResponse,
    FolderDetailResponse,
    FolderListResponse,
    FolderOpenResponse,
    FolderUpdateRequest,
    FolderUpdateResponse,
)
from src.core.constants import ERROR_FOLDER_NOT_FOUND
from src.services.folder_service import FolderService


router = APIRouter(
    prefix="/folders",
    tags=["folders"],
    dependencies=[ApiKeyDependency],
)


@router.post(
    "",
    response_model=FolderCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_folder(
    request: FolderCreateRequest,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderCreateResponse:
    try:
        folder = service.create_folder(
            name=request.name,
            description=request.description,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return FolderCreateResponse.from_record(folder)


@router.get("", response_model=list[FolderListResponse])
def list_folders(
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> list[FolderListResponse]:
    return [FolderListResponse.from_record(folder) for folder in service.list_folders()]


@router.get("/{folder_id}", response_model=FolderDetailResponse)
def get_folder(
    folder_id: UUID,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderDetailResponse:
    folder = service.get_folder(folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_FOLDER_NOT_FOUND,
        )
    return FolderDetailResponse.from_record(folder)


@router.patch("/{folder_id}/open", response_model=FolderOpenResponse)
def open_folder(
    folder_id: UUID,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderOpenResponse:
    try:
        folder = service.open_folder(folder_id)
    except ValueError as error:
        raise map_service_error(error) from error
    return FolderOpenResponse.from_record(folder)


@router.patch("/{folder_id}", response_model=FolderUpdateResponse)
def update_folder(
    folder_id: UUID,
    request: FolderUpdateRequest,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderUpdateResponse:
    try:
        # model_fields_set lets PATCH distinguish omitted fields from an explicit
        # JSON null, which is needed for clearing description without requiring name.
        folder = service.update_folder(
            folder_id=folder_id,
            name=request.name,
            description=request.description,
            update_description="description" in request.model_fields_set,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return FolderUpdateResponse.from_record(folder)


@router.delete("/{folder_id}", response_model=DeleteResponse)
def delete_folder(
    folder_id: UUID,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> DeleteResponse:
    try:
        service.delete_folder(folder_id)
    except ValueError as error:
        raise map_service_error(error) from error
    return DeleteResponse(deleted=True)
