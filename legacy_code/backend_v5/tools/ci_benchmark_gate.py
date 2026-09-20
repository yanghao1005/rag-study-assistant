from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmark_chat import run_chat_benchmark
from benchmark_generation import run_generation_benchmark
from benchmark_retrieval import run_retrieval_benchmark


def _profile_thresholds(profile: str) -> dict[str, float]:
    if profile == "prod":
        return {
            "max_retrieval_p95_ms": 800.0,
            "max_generation_p95_ms": 4000.0,
            "max_chat_p95_ms": 5000.0,
            "min_acceptance_ratio": 0.45,
            "min_schema_valid_rate": 1.0,
            "min_response_ok_rate": 1.0,
            "min_avg_best_score": 0.05,
            "min_chat_citation_rate": 0.85,
        }

    return {
        "max_retrieval_p95_ms": 1200.0,
        "max_generation_p95_ms": 6000.0,
        "max_chat_p95_ms": 7000.0,
        "min_acceptance_ratio": 0.30,
        "min_schema_valid_rate": 1.0,
        "min_response_ok_rate": 1.0,
        "min_avg_best_score": 0.01,
        "min_chat_citation_rate": 0.70,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v5 benchmark gates")
    parser.add_argument("--output-dir", default="backend_v5/benchmark_reports")
    parser.add_argument("--retrieval-iterations", type=int, default=12)
    parser.add_argument("--generation-iterations", type=int, default=12)
    parser.add_argument("--chat-iterations", type=int, default=12)
    parser.add_argument("--benchmark-profile", choices=["ci", "prod"], default="ci")
    parser.add_argument("--max-retrieval-p95-ms", type=float, default=None)
    parser.add_argument("--max-generation-p95-ms", type=float, default=None)
    parser.add_argument("--max-chat-p95-ms", type=float, default=None)
    parser.add_argument("--min-acceptance-ratio", type=float, default=None)
    parser.add_argument("--min-schema-valid-rate", type=float, default=None)
    parser.add_argument("--min-response-ok-rate", type=float, default=None)
    parser.add_argument("--min-avg-best-score", type=float, default=None)
    parser.add_argument("--min-chat-citation-rate", type=float, default=None)
    args = parser.parse_args()

    thresholds = _profile_thresholds(args.benchmark_profile)
    if args.max_retrieval_p95_ms is not None:
        thresholds["max_retrieval_p95_ms"] = args.max_retrieval_p95_ms
    if args.max_generation_p95_ms is not None:
        thresholds["max_generation_p95_ms"] = args.max_generation_p95_ms
    if args.max_chat_p95_ms is not None:
        thresholds["max_chat_p95_ms"] = args.max_chat_p95_ms
    if args.min_acceptance_ratio is not None:
        thresholds["min_acceptance_ratio"] = args.min_acceptance_ratio
    if args.min_schema_valid_rate is not None:
        thresholds["min_schema_valid_rate"] = args.min_schema_valid_rate
    if args.min_response_ok_rate is not None:
        thresholds["min_response_ok_rate"] = args.min_response_ok_rate
    if args.min_avg_best_score is not None:
        thresholds["min_avg_best_score"] = args.min_avg_best_score
    if args.min_chat_citation_rate is not None:
        thresholds["min_chat_citation_rate"] = args.min_chat_citation_rate

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    retrieval_report = run_retrieval_benchmark(iterations=max(1, args.retrieval_iterations))
    generation_report = run_generation_benchmark(iterations=max(1, args.generation_iterations))
    chat_report = run_chat_benchmark(iterations=max(1, args.chat_iterations))

    (output_dir / "retrieval_benchmark.json").write_text(json.dumps(retrieval_report, indent=2), encoding="utf-8")
    (output_dir / "generation_benchmark.json").write_text(json.dumps(generation_report, indent=2), encoding="utf-8")
    (output_dir / "chat_benchmark.json").write_text(json.dumps(chat_report, indent=2), encoding="utf-8")

    failures: list[str] = []
    if retrieval_report["retrieval_p95_ms"] > thresholds["max_retrieval_p95_ms"]:
        failures.append(
            f"retrieval_p95_ms={retrieval_report['retrieval_p95_ms']:.2f} exceeds {thresholds['max_retrieval_p95_ms']:.2f}"
        )
    if retrieval_report["avg_acceptance_ratio"] < thresholds["min_acceptance_ratio"]:
        failures.append(
            f"avg_acceptance_ratio={retrieval_report['avg_acceptance_ratio']:.4f} below {thresholds['min_acceptance_ratio']:.4f}"
        )
    if retrieval_report["avg_best_score"] < thresholds["min_avg_best_score"]:
        failures.append(
            f"avg_best_score={retrieval_report['avg_best_score']:.4f} below {thresholds['min_avg_best_score']:.4f}"
        )
    if generation_report["generation_p95_ms"] > thresholds["max_generation_p95_ms"]:
        failures.append(
            f"generation_p95_ms={generation_report['generation_p95_ms']:.2f} exceeds {thresholds['max_generation_p95_ms']:.2f}"
        )
    if generation_report["schema_valid_rate"] < thresholds["min_schema_valid_rate"]:
        failures.append(
            f"schema_valid_rate={generation_report['schema_valid_rate']:.4f} below {thresholds['min_schema_valid_rate']:.4f}"
        )
    if generation_report["response_ok_rate"] < thresholds["min_response_ok_rate"]:
        failures.append(
            f"response_ok_rate={generation_report['response_ok_rate']:.4f} below {thresholds['min_response_ok_rate']:.4f}"
        )
    if chat_report["chat_p95_ms"] > thresholds["max_chat_p95_ms"]:
        failures.append(
            f"chat_p95_ms={chat_report['chat_p95_ms']:.2f} exceeds {thresholds['max_chat_p95_ms']:.2f}"
        )
    if chat_report["citation_rate"] < thresholds["min_chat_citation_rate"]:
        failures.append(
            f"chat citation_rate={chat_report['citation_rate']:.4f} below {thresholds['min_chat_citation_rate']:.4f}"
        )

    combined = {
        "benchmark_profile": args.benchmark_profile,
        "retrieval": retrieval_report,
        "generation": generation_report,
        "chat": chat_report,
        "thresholds": thresholds,
        "passed": not failures,
        "failures": failures,
    }
    (output_dir / "benchmark_gate_report.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")

    print(json.dumps(combined, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
