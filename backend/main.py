"""FastAPI entry point for the NoteConnect backend."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import (
    folder_router,
    health_router,
    note_router,
    relation_router,
)
from src.core.config import get_config
from src.core.logging import configure_logging, install_request_logging
from src.services.explanation_generator import ExplanationGenerator
from src.services.explanation_service import ExplanationService
from src.services.folder_service import FolderService
from src.services.note_service import NoteService
from src.services.relation_query_service import RelationQueryService
from src.services.sentence_processor import SentenceProcessor


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build long-lived services once so AI models are reused across requests."""
    config = app.state.config if hasattr(app.state, "config") else get_config()
    configure_logging(config.log_level)
    logger.info(
        "Starting NoteConnect backend env=%s explanation_load_mode=%s",
        config.app_env,
        config.explanation_load_mode,
    )
    sentence_processor = SentenceProcessor(
        embedding_model_name=config.embedding_model,
        nli_model_name=config.nli_model,
        embedding_dimension=config.embedding_dimension,
    )
    explanation_generator = ExplanationGenerator(
        model_name=config.explanation_model,
        max_new_tokens=config.explanation_max_new_tokens,
        load_mode=config.explanation_load_mode,
    )
    # Startup mode keeps the explanation model resident for faster POST /explanation.
    # Lazy mode skips this load so small internal servers do not hold the LLM in RAM.
    if config.explanation_load_mode == "startup":
        explanation_generator.load()
    app.state.folder_service = FolderService(config=config)
    app.state.note_service = NoteService(
        config=config,
        sentence_processor=sentence_processor,
    )
    app.state.relation_query_service = RelationQueryService(config=config)
    app.state.explanation_service = ExplanationService(
        config=config,
        explanation_generator=explanation_generator,
    )
    logger.info("NoteConnect backend services are ready")
    yield
    logger.info("Stopping NoteConnect backend")


def create_app() -> FastAPI:
    """Create a FastAPI app configured for the current runtime environment."""
    config = get_config()
    configure_logging(config.log_level)
    app = FastAPI(
        title="NoteConnect API",
        lifespan=lifespan,
        docs_url="/docs" if config.enable_docs else None,
        redoc_url="/redoc" if config.enable_docs else None,
        openapi_url="/openapi.json" if config.enable_docs else None,
    )
    app.state.config = config
    install_request_logging(
        app,
        enabled=config.log_requests,
        slow_request_ms=config.slow_request_ms,
    )
    app.include_router(health_router.router)
    app.include_router(folder_router.router)
    app.include_router(note_router.router)
    app.include_router(relation_router.router)
    return app


app = create_app()
