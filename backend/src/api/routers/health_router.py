"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from src.api.schemas import HealthResponse, ReadyResponse
from src.core.config import get_config
from src.core.database import check_database_connection


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse)
def ready_check(request: Request) -> ReadyResponse:
    config = (
        request.app.state.config
        if hasattr(request.app.state, "config")
        else get_config()
    )
    database_status = "skipped"

    if config.ready_check_database:
        try:
            check_database_connection(config)
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is not ready.",
            ) from error
        database_status = "ready"

    return ReadyResponse(
        status="ready",
        database=database_status,
        explanation_load_mode=config.explanation_load_mode,
    )
