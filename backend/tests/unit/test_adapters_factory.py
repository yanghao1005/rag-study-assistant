"""Unit tests for chunker and provider factory."""

from __future__ import annotations

import pytest

from app.adapters.llm.factory import create_embedding_port, create_llm_port
from app.adapters.llm.gemini_llm import GeminiLLMAdapter
from app.adapters.llm.openai_embeddings import OpenAIEmbeddingAdapter
from app.adapters.llm.openai_llm import OpenAILLMAdapter
from app.adapters.parsing.semantic_chunker import SemanticChunkerAdapter
from app.core.config import Settings
from app.ports.parsing import ParsedDocument, ParsedPage


def test_semantic_chunker_splits_long_text() -> None:
    chunker = SemanticChunkerAdapter(max_chars=50, overlap_chars=10)
    document = ParsedDocument(
        pages=[
            ParsedPage(page_number=1, text="Alpha paragraph one.\n\nBeta paragraph two."),
            ParsedPage(page_number=2, text="Gamma paragraph three is a bit longer than others."),
        ],
        total_pages=2,
    )
    chunks = chunker.chunk(document)
    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert all(chunk.content.strip() for chunk in chunks)


def test_factory_openai_defaults() -> None:
    settings = Settings(  # type: ignore[call-arg]
        OPENAI_API_KEY="sk-test",
        LLM_PROVIDER="openai",
        EMBEDDING_PROVIDER="openai",
    )
    llm = create_llm_port(settings)
    emb = create_embedding_port(settings)
    assert isinstance(llm, OpenAILLMAdapter)
    assert isinstance(emb, OpenAIEmbeddingAdapter)
    assert emb.dimensions == 1536


def test_factory_gemini_llm() -> None:
    settings = Settings(  # type: ignore[call-arg]
        GOOGLE_AI_API_KEY="test-key",
        LLM_PROVIDER="gemini",
        EMBEDDING_PROVIDER="openai",
        OPENAI_API_KEY="sk-test",
    )
    llm = create_llm_port(settings)
    assert isinstance(llm, GeminiLLMAdapter)


def test_factory_rejects_unknown_llm() -> None:
    settings = Settings(  # type: ignore[call-arg]
        OPENAI_API_KEY="sk-test",
        LLM_PROVIDER="openai",
    )
    object.__setattr__(settings, "llm_provider", "anthropic")  # bypass literal for test
    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        create_llm_port(settings)
