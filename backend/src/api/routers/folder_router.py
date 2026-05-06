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
from src.api.schemas import DeleteResponse, FolderCreateRequest, FolderResponse
from src.services.folder_service import FolderService


router = APIRouter(
    prefix="/folders",
    tags=["folders"],
    dependencies=[ApiKeyDependency],
)


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_folder(
    request: FolderCreateRequest,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderResponse:
    try:
        folder = service.create_folder(
            name=request.name,
            description=request.description,
        )
    except ValueError as error:
        raise map_service_error(error) from error
    return FolderResponse.from_record(folder)


@router.get("", response_model=list[FolderResponse])
def list_folders(
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> list[FolderResponse]:
    return [FolderResponse.from_record(folder) for folder in service.list_folders()]


@router.get("/{folder_id}", response_model=FolderResponse)
def get_folder(
    folder_id: UUID,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderResponse:
    folder = service.get_folder(folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found.",
        )
    return FolderResponse.from_record(folder)


@router.patch("/{folder_id}/open", response_model=FolderResponse)
def open_folder(
    folder_id: UUID,
    service: Annotated[FolderService, Depends(get_folder_service)],
) -> FolderResponse:
    try:
        folder = service.open_folder(folder_id)
    except ValueError as error:
        raise map_service_error(error) from error
    return FolderResponse.from_record(folder)


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
