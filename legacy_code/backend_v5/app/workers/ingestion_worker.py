from __future__ import annotations

import time
from dataclasses import dataclass

from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.infrastructure.memory_repository import InMemoryRepository


@dataclass
class IngestionWorker:
    repository: InMemoryRepository
    pipeline_use_case: PipelineUseCase
    poll_interval_seconds: float = 1.0

    def run_once(self, *, max_jobs: int = 10) -> int:
        queued_jobs = self.repository.list_queued_jobs(limit=max_jobs)
        processed = 0
        for job in queued_jobs:
            self.repository.update_job(job_id=job["id"], status="running")
            try:
                payload = job.get("payload", {})
                document_id = payload.get("document_id", "")
                self.pipeline_use_case.ingest_document(
                    user_id=job["user_id"],
                    document_id=document_id,
                    job_id=job["id"],
                )
                self.repository.update_job(
                    job_id=job["id"],
                    status="completed",
                    result={"document_id": document_id},
                )
                processed += 1
            except Exception as exc:  # pragma: no cover - defensive fallback
                self.repository.update_job(
                    job_id=job["id"],
                    status="failed",
                    error_message=str(exc),
                )
        return processed

    def run_forever(self, *, max_jobs: int = 10) -> None:
        while True:
            self.run_once(max_jobs=max_jobs)
            time.sleep(self.poll_interval_seconds)

