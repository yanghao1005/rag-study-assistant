"""Retrieval / generation latency harness (debug-friendly, no live I/O required)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from app.ports.llm import EmbeddingPort
from app.ports.retrieval import RetrievalFilters, VectorSearchPort


@dataclass(slots=True)
class BenchmarkCase:
    name: str
    query: str
    subject_id: str
    user_id: str = "bench-user"
    document_id: str | None = None


@dataclass(slots=True)
class BenchmarkResult:
    name: str
    duration_ms: int
    retrieved: int
    extra: dict[str, Any] = field(default_factory=dict)


async def run_retrieval_benchmark(
    *,
    cases: list[BenchmarkCase],
    retrieval: VectorSearchPort,
    embeddings: EmbeddingPort,
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    for case in cases:
        started = time.perf_counter()
        vectors = await embeddings.embed([case.query])
        found = await retrieval.hybrid_search(
            query_text=case.query,
            query_embedding=vectors[0],
            filters=RetrievalFilters(
                user_id=case.user_id,
                subject_id=case.subject_id,
                document_id=case.document_id,
            ),
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        results.append(
            BenchmarkResult(
                name=case.name,
                duration_ms=duration_ms,
                retrieved=len(found.chunks),
                extra={"dense": len(found.dense_ids), "lexical": len(found.lexical_ids)},
            )
        )
    return results


def summarize(results: list[BenchmarkResult]) -> dict[str, Any]:
    if not results:
        return {"count": 0, "p50_ms": 0, "max_ms": 0, "mean_retrieved": 0}
    durations = [item.duration_ms for item in results]
    durations.sort()
    mid = durations[len(durations) // 2]
    retrieved = [item.retrieved for item in results]
    return {
        "count": len(results),
        "p50_ms": mid,
        "max_ms": max(durations),
        "mean_retrieved": round(sum(retrieved) / len(retrieved), 2),
        "cases": [
            {"name": item.name, "duration_ms": item.duration_ms, "retrieved": item.retrieved}
            for item in results
        ],
    }
