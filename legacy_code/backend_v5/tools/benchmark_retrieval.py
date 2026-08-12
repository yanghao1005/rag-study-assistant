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


def run_retrieval_benchmark(*, iterations: int = 12) -> dict:
    client, headers = _build_client()

    upload = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "benchmark-subject",
            "title": "Retrieval Benchmark Summary",
            "content": (
                "Neural networks learn through weighted connections and activation functions. "
                "Backpropagation updates weights to reduce prediction error. "
                "Convolutional layers are useful for spatial patterns in image data."
            ),
        },
        headers=headers,
    )
    if upload.status_code != 200:
        raise RuntimeError(f"Failed to setup retrieval benchmark fixture: {upload.status_code} {upload.text}")
    document_id = upload.json()["document_id"]

    latencies_ms: list[float] = []
    best_scores: list[float] = []
    coverage_ratios: list[float] = []

    for _ in range(iterations):
        started = time.perf_counter()
        response = client.post(
            "/api/generate/flashcards",
            json={
                "scope": "document",
                "scope_id": document_id,
                "query": "How do neural networks learn?",
                "count": 3,
                "save": False,
            },
            headers=headers,
        )
        latencies_ms.append((time.perf_counter() - started) * 1000.0)

        if response.status_code != 200:
            raise RuntimeError(f"Retrieval benchmark request failed: {response.status_code} {response.text}")

        payload = response.json()
        diagnostics = payload.get("diagnostics") or {}
        best_scores.append(float(diagnostics.get("best_score") or 0.0))
        total = float(diagnostics.get("total_candidates") or 0.0)
        accepted = float(diagnostics.get("accepted_candidates") or 0.0)
        coverage_ratios.append((accepted / total) if total > 0 else 0.0)

    return {
        "benchmark": "retrieval",
        "iterations": iterations,
        "retrieval_p95_ms": _p95(latencies_ms),
        "avg_best_score": (sum(best_scores) / len(best_scores)) if best_scores else 0.0,
        "avg_acceptance_ratio": (sum(coverage_ratios) / len(coverage_ratios)) if coverage_ratios else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v5 retrieval benchmark")
    parser.add_argument("--output", default="backend_v5/benchmark_reports/retrieval_benchmark.json")
    parser.add_argument("--iterations", type=int, default=12)
    args = parser.parse_args()

    report = run_retrieval_benchmark(iterations=max(1, args.iterations))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
