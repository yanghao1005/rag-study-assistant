"""CLI: python -m app.entrypoints.cli.benchmark"""

from __future__ import annotations

import argparse
import asyncio
import json

from app.application.benchmark import BenchmarkCase, run_retrieval_benchmark, summarize
from app.container import build_container
from app.core.config import get_settings


async def _run(args: argparse.Namespace) -> None:
    settings = get_settings()
    container = build_container(settings)
    cases = [
        BenchmarkCase(
            name=f"q{index}",
            query=query,
            subject_id=args.subject_id,
            user_id=args.user_id,
        )
        for index, query in enumerate(args.query, start=1)
    ]
    results = await run_retrieval_benchmark(
        cases=cases,
        retrieval=container.retrieval,
        embeddings=container.embeddings,
    )
    print(json.dumps(summarize(results), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark hybrid retrieval latency.")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--query", action="append", required=True, help="Repeatable query")
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
