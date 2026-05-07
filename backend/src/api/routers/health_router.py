"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
