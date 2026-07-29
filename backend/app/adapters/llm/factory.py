"""Provider factories for LLM and embedding adapters."""

from __future__ import annotations

from app.adapters.llm.gemini_llm import GeminiLLMAdapter
from app.adapters.llm.openai_embeddings import OpenAIEmbeddingAdapter
from app.adapters.llm.openai_llm import OpenAILLMAdapter
from app.core.config import Settings
from app.ports.llm import EmbeddingPort, LLMPort


def create_embedding_port(settings: Settings) -> EmbeddingPort:
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            dimensions=settings.openai_embedding_dimensions,
        )
    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER={settings.embedding_provider!r}. "
        "Only 'openai' is supported while the schema uses vector(1536)."
    )


def create_llm_port(settings: Settings) -> LLMPort:
    if settings.llm_provider == "openai":
        return OpenAILLMAdapter(api_key=settings.openai_api_key, model=settings.openai_model)
    if settings.llm_provider == "gemini":
        return GeminiLLMAdapter(api_key=settings.google_ai_api_key, model=settings.gemini_model)
    raise ValueError(f"Unsupported LLM_PROVIDER={settings.llm_provider!r}")
