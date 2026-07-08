from __future__ import annotations

from functools import lru_cache

from app.application.services.retrieval_service import RetrievalService
from app.application.use_cases.chat_use_case import ChatUseCase
from app.application.use_cases.documents_use_case import DocumentsUseCase
from app.application.use_cases.generation_use_case import GenerationUseCase
from app.application.use_cases.jobs_use_case import JobsUseCase
from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.core.config import get_settings
from app.infrastructure.memory_repository import InMemoryRepository


@lru_cache(maxsize=1)
def get_repository() -> InMemoryRepository:
    # Baseline implementation uses in-memory repository.
    # Supabase adapters can be plugged in later behind this boundary.
    _settings = get_settings()
    return InMemoryRepository()


@lru_cache(maxsize=1)
def get_pipeline_use_case() -> PipelineUseCase:
    return PipelineUseCase(repository=get_repository())


@lru_cache(maxsize=1)
def get_documents_use_case() -> DocumentsUseCase:
    return DocumentsUseCase(
        repository=get_repository(),
        pipeline_use_case=get_pipeline_use_case(),
        settings=get_settings(),
    )


@lru_cache(maxsize=1)
def get_jobs_use_case() -> JobsUseCase:
    return JobsUseCase(repository=get_repository())


@lru_cache(maxsize=1)
def get_generation_use_case() -> GenerationUseCase:
    return GenerationUseCase(
        repository=get_repository(),
        retrieval_service=RetrievalService(),
    )


@lru_cache(maxsize=1)
def get_chat_use_case() -> ChatUseCase:
    return ChatUseCase(repository=get_repository())

