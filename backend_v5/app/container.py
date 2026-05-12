from functools import lru_cache

from app.application.use_cases.chat_use_case import ChatUseCase
from app.application.use_cases.documents_use_case import DocumentsUseCase
from app.application.use_cases.generation_use_case import GenerationUseCase
from app.application.use_cases.jobs_use_case import JobsUseCase
from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.application.services.retrieval_service import RetrievalService
from app.core.config import get_settings
from app.core.errors import AppError
from app.infrastructure.parsing.pdf_parser import PDFParser
from app.infrastructure.parsing.semantic_chunker import SemanticChunker
from app.infrastructure.persistence.memory_repository import InMemoryStudyRepository
from app.infrastructure.persistence.supabase.study_repository import SupabaseStudyRepository


@lru_cache(maxsize=1)
def get_repository():
    settings = get_settings()
    if settings.vector_repository_provider == "supabase":
        if not settings.supabase_url or not settings.supabase_service_key:
            raise AppError(
                error="supabase_not_configured",
                message="SUPABASE_URL and SUPABASE_SERVICE_KEY are required when VECTOR_REPOSITORY_PROVIDER=supabase.",
                status_code=503,
            )
        return SupabaseStudyRepository()
    return InMemoryStudyRepository()


@lru_cache(maxsize=1)
def get_pipeline_use_case() -> PipelineUseCase:
    return PipelineUseCase(repository=get_repository(), pdf_parser=PDFParser(), chunker=SemanticChunker())


@lru_cache(maxsize=1)
def get_documents_use_case() -> DocumentsUseCase:
    settings = get_settings()
    return DocumentsUseCase(
        repository=get_repository(),
        pipeline_use_case=get_pipeline_use_case(),
        uploads_dir=settings.uploads_dir,
        enable_async_ingestion=settings.enable_async_ingestion,
    )


@lru_cache(maxsize=1)
def get_jobs_use_case() -> JobsUseCase:
    return JobsUseCase(repository=get_repository())


@lru_cache(maxsize=1)
def get_generation_use_case() -> GenerationUseCase:
    return GenerationUseCase(repository=get_repository(), retrieval_service=RetrievalService(repository=get_repository()))


@lru_cache(maxsize=1)
def get_chat_use_case() -> ChatUseCase:
    return ChatUseCase(repository=get_repository(), retrieval_service=RetrievalService(repository=get_repository()))
