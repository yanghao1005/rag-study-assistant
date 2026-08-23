"""Stage-selectable ingestion CLI: python -m app.entrypoints.cli.pipeline ..."""

from __future__ import annotations

import argparse
import asyncio
import json
from uuid import uuid4

from app.container import build_container
from app.core.config import get_settings
from app.domain.entities.enums import JobStatus, JobType, PipelineStage
from app.domain.entities.job import Job


async def _run(args: argparse.Namespace) -> None:
    settings = get_settings()
    container = build_container(settings)
    document = await container.documents.get(user_id=args.user_id, document_id=args.document_id)
    if document is None:
        raise SystemExit(f"Document not found: {args.document_id}")
    job = await container.jobs.create(
        Job(
            id=str(uuid4()),
            user_id=args.user_id,
            job_type=JobType.REINDEX_DOCUMENT,
            status=JobStatus.QUEUED,
            subject_id=document.subject_id,
            document_id=document.id,
            payload={"cli": True, "from_stage": args.from_stage, "to_stage": args.to_stage},
        )
    )
    completed = await container.ingestion_pipeline.run_range(
        job,
        from_stage=PipelineStage(args.from_stage),
        to_stage=PipelineStage(args.to_stage),
    )
    print(
        json.dumps(
            {
                "job_id": completed.id,
                "status": completed.status.value,
                "result": completed.result,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ingestion pipeline stages for a document.")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--from-stage", default="download")
    parser.add_argument("--to-stage", default="synopsis")
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
