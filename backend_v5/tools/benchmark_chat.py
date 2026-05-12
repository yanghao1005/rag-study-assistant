from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import jwt
from fastapi.testclient import TestClient


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, int(round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def _build_client() -> tuple[TestClient, dict[str, str]]:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in os.sys.path:
        os.sys.path.insert(0, str(backend_root))

    os.environ.setdefault("SUPABASE_JWT_SECRET", "benchmark-secret")
    os.environ.setdefault("VECTOR_REPOSITORY_PROVIDER", "memory")
    os.environ.setdefault("ENABLE_ASYNC_INGESTION", "false")
    os.environ.setdefault("LLM_PROVIDER", "openai")

    from app import container
    from app.core.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    container.get_repository.cache_clear()
    container.get_pipeline_use_case.cache_clear()
    container.get_documents_use_case.cache_clear()
    container.get_jobs_use_case.cache_clear()
    container.get_generation_use_case.cache_clear()
    container.get_chat_use_case.cache_clear()

    app = create_app()
    client = TestClient(app)
    token = jwt.encode({"sub": "benchmark-user", "role": "authenticated"}, "benchmark-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers


def run_chat_benchmark(*, iterations: int = 12) -> dict:
    client, headers = _build_client()

    upload = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "benchmark-subject",
            "title": "Chat Benchmark Summary",
            "content": (
                "Neural network learning typically uses backpropagation and gradient descent. "
                "The loss function guides updates to model parameters."
            ),
        },
        headers=headers,
    )
    if upload.status_code != 200:
        raise RuntimeError(f"Failed to setup chat benchmark fixture: {upload.status_code} {upload.text}")
    document_id = upload.json()["document_id"]

    latencies_ms: list[float] = []
    answers_ok = 0
    citation_hits = 0
    confidence_values: list[float] = []

    for _ in range(iterations):
        started = time.perf_counter()
        response = client.post(
            "/api/chat/ask",
            json={
                "scope": "document",
                "scope_id": document_id,
                "question": "How does neural network learning work?",
            },
            headers=headers,
        )
        latencies_ms.append((time.perf_counter() - started) * 1000.0)

        if response.status_code != 200:
            raise RuntimeError(f"Chat benchmark request failed: {response.status_code} {response.text}")

        payload = response.json()
        answer = payload.get("answer")
        citations = payload.get("citations")
        confidence = payload.get("confidence")

        if isinstance(answer, str) and answer.strip():
            answers_ok += 1
        if isinstance(citations, list) and len(citations) > 0:
            citation_hits += 1
        if isinstance(confidence, (int, float)):
            confidence_values.append(float(confidence))

    return {
        "benchmark": "chat",
        "iterations": iterations,
        "chat_p95_ms": _p95(latencies_ms),
        "answer_ok_rate": answers_ok / float(iterations),
        "citation_rate": citation_hits / float(iterations),
        "avg_confidence": (sum(confidence_values) / len(confidence_values)) if confidence_values else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v5 chat benchmark")
    parser.add_argument("--output", default="backend_v5/benchmark_reports/chat_benchmark.json")
    parser.add_argument("--iterations", type=int, default=12)
    args = parser.parse_args()

    report = run_chat_benchmark(iterations=max(1, args.iterations))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
