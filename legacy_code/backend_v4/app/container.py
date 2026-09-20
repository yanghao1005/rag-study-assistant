from functools import lru_cache
import logging

from app.application.use_cases.generation_service import GenerationService
from app.application.use_cases.pipeline_runner import PipelineRunner
from app.core.config import get_settings
from app.domain.ports.providers import EmbeddingsProvider as EmbeddingsProviderPort
from app.domain.ports.providers import LLMProvider as LLMProviderPort
from app.domain.ports.repositories import VectorRepository
from app.infrastructure.parsing.pdf_parser import PDFParser
from app.infrastructure.providers.embeddings_provider import EmbeddingsProvider as StubEmbeddingsProvider
from app.infrastructure.providers.llm_provider import LLMProvider as StubLLMProvider
from app.infrastructure.providers.openai_embeddings_provider import OpenAIEmbeddingsProvider
from app.infrastructure.providers.openai_llm_provider import OpenAILLMProvider
from app.infrastructure.repositories.supabase_repository import SupabaseVectorRepository
from app.infrastructure.repositories.vector_repository import InMemoryVectorRepository

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_vector_repository() -> VectorRepository:
    settings = get_settings()

    if settings.vector_repository_provider == "supabase":
        key = settings.supabase_service_key or settings.supabase_key
        if settings.supabase_url and key:
            try:
                return SupabaseVectorRepository(
                    url=settings.supabase_url,
                    key=key,
                    generated_table=settings.supabase_generated_table,
                    chunks_table=settings.supabase_chunks_table,
                )
            except Exception as exc:
                logger.warning("Supabase repository unavailable, falling back to memory: %s", exc)

    return InMemoryVectorRepository()


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProviderPort:
    settings = get_settings()
    base_url = settings.openai_base_url or None

    if settings.llm_provider == "openai" and settings.openai_api_key:
        try:
            return OpenAILLMProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_llm_model,
                base_url=base_url,
            )
        except Exception as exc:
            logger.warning("OpenAI LLM provider unavailable, falling back to stub: %s", exc)

    return StubLLMProvider()


@lru_cache(maxsize=1)
def get_embeddings_provider() -> EmbeddingsProviderPort:
    settings = get_settings()
    base_url = settings.openai_base_url or None

    if settings.embeddings_provider == "openai" and settings.openai_api_key:
        try:
            return OpenAIEmbeddingsProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_embedding_model,
                base_url=base_url,
            )
        except Exception as exc:
            logger.warning("OpenAI embeddings provider unavailable, falling back to stub: %s", exc)

    return StubEmbeddingsProvider()


@lru_cache(maxsize=1)
def get_generation_service() -> GenerationService:
    settings = get_settings()
    return GenerationService(
        vector_repository=get_vector_repository(),
        llm_provider=get_llm_provider(),
        debug_artifacts_dir=settings.debug_artifacts_dir,
    )


@lru_cache(maxsize=1)
def get_pdf_parser() -> PDFParser:
    return PDFParser()


@lru_cache(maxsize=1)
def get_pipeline_runner() -> PipelineRunner:
    settings = get_settings()
    return PipelineRunner(
        vector_repository=get_vector_repository(),
        embeddings_provider=get_embeddings_provider(),
        pdf_parser=get_pdf_parser(),
        artifacts_dir=settings.debug_artifacts_dir,
    )