"""FastAPI entry point for the NoteConnect backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routers import (
    folder_router,
    health_router,
    note_router,
    relation_router,
)
from src.core.config import get_config
from src.services.explanation_generator import ExplanationGenerator
from src.services.explanation_service import ExplanationService
from src.services.folder_service import FolderService
from src.services.note_service import NoteService
from src.services.relation_query_service import RelationQueryService
from src.services.sentence_processor import SentenceProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build long-lived services once so AI models are reused across requests."""
    config = get_config()
    sentence_processor = SentenceProcessor(
        embedding_model_name=config.embedding_model,
        nli_model_name=config.nli_model,
        embedding_dimension=config.embedding_dimension,
    )
    explanation_generator = ExplanationGenerator(
        model_name=config.explanation_model,
        max_new_tokens=config.explanation_max_new_tokens,
    )
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
    yield


app = FastAPI(title="NoteConnect API", lifespan=lifespan)

app.include_router(health_router.router)
app.include_router(folder_router.router)
app.include_router(note_router.router)
app.include_router(relation_router.router)
