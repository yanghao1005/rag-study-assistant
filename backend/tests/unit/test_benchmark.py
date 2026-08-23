"""Benchmark harness tests (no live providers)."""

from __future__ import annotations

import asyncio

from app.application.benchmark import BenchmarkCase, run_retrieval_benchmark, summarize
from tests.fakes import FakeEmbeddings, FakeRetrieval


def test_retrieval_benchmark_summarizes() -> None:
    results = asyncio.run(
        run_retrieval_benchmark(
            cases=[
                BenchmarkCase(name="q1", query="ATP", subject_id="s1"),
            ],
            retrieval=FakeRetrieval(),
            embeddings=FakeEmbeddings(),
        )
    )
    summary = summarize(results)
    assert summary["count"] == 1
    assert results[0].retrieved == 1
    assert "p50_ms" in summary
