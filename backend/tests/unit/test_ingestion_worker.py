"""Unit tests for the background ingestion worker loop."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings
from app.domain.entities.enums import JobStatus, JobType
from app.domain.entities.job import Job
from app.entrypoints.workers.ingestion_worker import IngestionWorker
from tests.fakes import FakeJobs


class _FakePipeline:
    def __init__(self) -> None:
        self.processed: list[str] = []

    async def process_job(self, job: Job) -> Job:
        self.processed.append(job.id)
        job.mark_completed(now=datetime.now(UTC), result={})
        return job


class _BoomThenEmptyJobs(FakeJobs):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    async def claim_next(self, *, job_types: list[str] | None = None) -> Job | None:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("transient claim failure")
        return await super().claim_next(job_types=job_types)


def _settings(**overrides: Any) -> Settings:
    return Settings(  # type: ignore[call-arg]
        APP_NAME="Test API",
        WORKER_POLL_INTERVAL_SECONDS=0.01,
        ENABLE_ASYNC_INGESTION=True,
        **overrides,
    )


async def _run_briefly(worker: IngestionWorker, seconds: float = 0.05) -> None:
    task = asyncio.create_task(worker.run_forever())
    await asyncio.sleep(seconds)
    worker.stop()
    await asyncio.wait_for(task, timeout=1)


def test_worker_fails_orphan_job_and_processes_next() -> None:
    jobs = FakeJobs()
    pipeline = _FakePipeline()
    orphan = Job(
        id="orphan",
        user_id="u1",
        job_type=JobType.INGEST_DOCUMENT,
        status=JobStatus.QUEUED,
        document_id=None,
        created_at=datetime(2020, 1, 1, tzinfo=UTC),
    )
    real = Job(
        id="real",
        user_id="u1",
        job_type=JobType.INGEST_DOCUMENT,
        status=JobStatus.QUEUED,
        document_id="doc-1",
        created_at=datetime.now(UTC),
    )
    asyncio.run(jobs.create(orphan))
    asyncio.run(jobs.create(real))

    worker = IngestionWorker(jobs=jobs, pipeline=pipeline, settings=_settings())  # type: ignore[arg-type]
    asyncio.run(_run_briefly(worker))

    assert jobs.items["orphan"].status == JobStatus.FAILED
    assert pipeline.processed == ["real"]


def test_worker_survives_claim_errors() -> None:
    jobs = _BoomThenEmptyJobs()
    pipeline = _FakePipeline()
    worker = IngestionWorker(jobs=jobs, pipeline=pipeline, settings=_settings())  # type: ignore[arg-type]
    asyncio.run(_run_briefly(worker))

    assert jobs.calls >= 2
    assert pipeline.processed == []
