"""API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.entrypoints.api.routes import (
    chat,
    debug,
    documents,
    generation,
    health,
    jobs,
    planner,
    profile,
    subjects,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(profile.router)
api_router.include_router(subjects.router)
api_router.include_router(documents.router)
api_router.include_router(jobs.router)
api_router.include_router(chat.router)
api_router.include_router(generation.router)
api_router.include_router(planner.router)
api_router.include_router(debug.router)
