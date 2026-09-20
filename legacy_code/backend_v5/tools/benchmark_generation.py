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


def _is_valid_quiz_item(item: dict) -> bool:
    question = item.get("question")
    options = item.get("options")
    correct = item.get("correct_answer")
    explanation = item.get("explanation")
    return (
        isinstance(question, str)
        and bool(question.strip())
        and isinstance(options, list)
        and len(options) == 4
        and isinstance(correct, int)
        and 0 <= correct <= 3
        and isinstance(explanation, str)
        and bool(explanation.strip())
    )


def run_generation_benchmark(*, iterations: int = 12) -> dict:
    client, headers = _build_client()

    upload = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "benchmark-subject",
            "title": "Generation Benchmark Summary",
            "content": (
                "Gradient descent minimizes loss by moving parameters opposite the gradient. "
                "Learning rate controls step size and convergence stability."
            ),
        },
        headers=headers,
    )
    if upload.status_code != 200:
        raise RuntimeError(f"Failed to setup generation benchmark fixture: {upload.status_code} {upload.text}")
    document_id = upload.json()["document_id"]

    latencies_ms: list[float] = []
    valid_payloads = 0
    valid_questions = 0
    total_questions = 0

    for _ in range(iterations):
        started = time.perf_counter()
        response = client.post(
            "/api/generate/quiz",
            json={
                "scope": "document",
                "scope_id": document_id,
                "query": "gradient descent",
                "count": 4,
                "save": False,
            },
            headers=headers,
        )
        latencies_ms.append((time.perf_counter() - started) * 1000.0)

        if response.status_code != 200:
            raise RuntimeError(f"Generation benchmark request failed: {response.status_code} {response.text}")

        payload = response.json()
        questions = payload.get("questions")
        if isinstance(questions, list):
            valid_payloads += 1
            for item in questions:
                if isinstance(item, dict):
                    total_questions += 1
                    if _is_valid_quiz_item(item):
                        valid_questions += 1

    schema_valid_rate = (valid_questions / total_questions) if total_questions > 0 else 0.0

    return {
        "benchmark": "generation",
        "iterations": iterations,
        "generation_p95_ms": _p95(latencies_ms),
        "response_ok_rate": valid_payloads / float(iterations),
        "schema_valid_rate": schema_valid_rate,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v5 generation benchmark")
    parser.add_argument("--output", default="backend_v5/benchmark_reports/generation_benchmark.json")
    parser.add_argument("--iterations", type=int, default=12)
    args = parser.parse_args()

    report = run_generation_benchmark(iterations=max(1, args.iterations))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
