from fastapi import APIRouter

from app.api.v1.routes import documents, generate, health, pipeline

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(generate.router, prefix="/generate", tags=["generate"])
