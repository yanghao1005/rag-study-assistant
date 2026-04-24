from __future__ import annotations

import argparse
import statistics
import time
from datetime import datetime, timezone

import httpx

from app.core.artifacts import write_json_artifact
from app.core.config import get_settings


def percentile95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(0.95 * (len(ordered) - 1))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark generation endpoint latency and record p95")
    parser.add_argument("--base-url", default="http://localhost:8000/api", help="API base URL")
    parser.add_argument("--iterations", type=int, default=10, help="Number of benchmark requests")
    parser.add_argument("--endpoint", choices=["flashcards", "quiz"], default="flashcards")
    args = parser.parse_args()

    payload = {
        "scope": "subject",
        "scope_id": "benchmark-subject",
        "count": 3,
        "query": "benchmark query",
        "debug": True,
    }

    latencies_ms: list[float] = []
    errors: list[str] = []

    for _ in range(args.iterations):
        start = time.perf_counter()
        try:
            response = httpx.post(
                f"{args.base_url}/generate/{args.endpoint}",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
        except Exception as exc:
            errors.append(str(exc))
        finally:
            latencies_ms.append((time.perf_counter() - start) * 1000)

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": args.endpoint,
        "iterations": args.iterations,
        "successful": args.iterations - len(errors),
        "failed": len(errors),
        "latencies_ms": latencies_ms,
        "p50_ms": statistics.median(latencies_ms) if latencies_ms else 0.0,
        "p95_ms": percentile95(latencies_ms),
        "errors": errors,
    }

    settings = get_settings()
    run_id = datetime.now(timezone.utc).strftime("benchmark-%Y%m%dT%H%M%SZ")
    report_path = write_json_artifact(
        root_dir=settings.benchmark_reports_dir,
        run_id=run_id,
        name=f"generation_{args.endpoint}",
        payload=report,
    )

    print(f"Benchmark report saved: {report_path}")
    print(f"p95 latency: {report['p95_ms']:.2f} ms")


if __name__ == "__main__":
    main()
