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

    try:
        model_statuses = _check_model_readiness(request)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not ready.",
        ) from error

    return ReadyResponse(
        status="ready",
        database=database_status,
        explanation_load_mode=config.explanation_load_mode,
        model_verified_loadable=model_statuses["model_verified_loadable"],
        embedding_model_status=model_statuses["embedding_model_status"],
        nli_model_status=model_statuses["nli_model_status"],
        explanation_model_status=model_statuses["explanation_model_status"],
    )


def _check_model_readiness(request: Request) -> dict[str, str | bool]:
    note_service = getattr(request.app.state, "note_service", None)
    explanation_service = getattr(request.app.state, "explanation_service", None)

    sentence_statuses = (
        note_service.model_statuses()
        if note_service is not None
        else {"embedding": "not_loaded", "nli": "not_loaded"}
    )

    if explanation_service is None:
        explanation_verified = False
        explanation_status = "not_loaded"
    else:
        # Lazy mode proves the local model can be loaded, then releases it so
        # readiness checks do not turn into permanent RAM usage.
        explanation_verified = explanation_service.verify_model_loadable()
        explanation_status = explanation_service.model_status()

    model_verified_loadable = (
        sentence_statuses["embedding"] == "loaded"
        and sentence_statuses["nli"] == "loaded"
        and explanation_verified
    )
    if not model_verified_loadable:
        raise RuntimeError("One or more models are not ready.")

    return {
        "model_verified_loadable": model_verified_loadable,
        "embedding_model_status": sentence_statuses["embedding"],
        "nli_model_status": sentence_statuses["nli"],
        "explanation_model_status": explanation_status,
    }
