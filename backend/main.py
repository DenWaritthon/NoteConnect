"""FastAPI entry point for the NoteConnect backend."""

from __future__ import annotations

from fastapi import FastAPI

from src.api.routers import (
    folder_router,
    health_router,
    note_router,
    relation_router,
)


app = FastAPI(title="NoteConnect API")

app.include_router(health_router.router)
app.include_router(folder_router.router)
app.include_router(note_router.router)
app.include_router(relation_router.router)
