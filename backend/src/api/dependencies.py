"""Reusable FastAPI dependencies for API authentication and services."""

from __future__ import annotations

from secrets import compare_digest

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import get_config
from src.services.folder_service import FolderService
from src.services.note_service import NoteService
from src.services.relation_query_service import RelationQueryService


_CONFIG = get_config()
_API_KEY_HEADER = APIKeyHeader(
    name=_CONFIG.api_key_header_name,
    auto_error=False,
)


def require_api_key(api_key: str | None = Security(_API_KEY_HEADER)) -> None:
    """Reject requests without the configured API key header."""
    config = get_config()
    expected_key = config.api_secret_key
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API secret key is not configured.",
        )

    if api_key is None or not compare_digest(api_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )


def get_folder_service() -> FolderService:
    return FolderService()


def get_note_service() -> NoteService:
    return NoteService()


def get_relation_query_service() -> RelationQueryService:
    return RelationQueryService()


def map_service_error(error: ValueError) -> HTTPException:
    """Convert service-layer validation errors into safe API errors."""
    message = str(error)
    status_code = (
        status.HTTP_404_NOT_FOUND
        if "not found" in message.lower()
        else status.HTTP_400_BAD_REQUEST
    )
    return HTTPException(status_code=status_code, detail=message)


ApiKeyDependency = Depends(require_api_key)
