"""API v1 router"""
from fastapi import APIRouter
from app.api.v1 import subjects, documents, search, generate

api_router = APIRouter()

api_router.include_router(subjects.router)
api_router.include_router(documents.router)
api_router.include_router(search.router)
api_router.include_router(generate.router)
