"""Unit tests for LLM rerank helper."""

from __future__ import annotations

import asyncio

from app.adapters.retrieval.llm_rerank import llm_rerank_chunks
from app.ports.llm import StructuredGenerationResult
from app.ports.retrieval import RetrievedChunk
from tests.fakes import FakeLLM


def _chunk(i: int) -> RetrievedChunk:
    return RetrievedChunk(
        id=f"c{i}",
        document_id="d1",
        subject_id="s1",
        chunk_index=i,
        content=f"passage {i}",
        score=float(i),
    )


def test_llm_rerank_reorders() -> None:
    llm = FakeLLM()

    async def complete_json(**_kwargs: object) -> StructuredGenerationResult:
        return StructuredGenerationResult(data={"order": [2, 1]}, model="fake", usage={})

    llm.complete_json = complete_json  # type: ignore[method-assign]
    chunks = [_chunk(1), _chunk(2)]
    ranked = asyncio.run(llm_rerank_chunks(llm, query="q", chunks=chunks, top_k=2))
    assert [c.id for c in ranked] == ["c2", "c1"]
