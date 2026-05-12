from __future__ import annotations

import argparse
import time
from typing import Any

from app.container import get_pipeline_use_case, get_repository
from app.core.config import get_settings
from app.domain.ports.repositories import StudyRepository


class IngestionWorker:
    def __init__(
        self,
        *,
        repository: StudyRepository,
        pipeline_use_case: Any | None = None,
        poll_interval_seconds: float = 1.0,
        job_types: tuple[str, ...] = ("ingest_document", "ingest_summary"),
    ) -> None:
        self._repository = repository
        self._pipeline = pipeline_use_case or get_pipeline_use_case()
        self._poll_interval_seconds = max(poll_interval_seconds, 0.1)
        self._job_types = list(job_types)

    def run_once(self, *, max_jobs: int = 1) -> int:
        processed = 0
        for _ in range(max_jobs):
            job = self._repository.claim_next_job(job_types=self._job_types)
            if not job:
                break
            self._process_job(job)
            processed += 1
        return processed

    def run_forever(self, *, max_jobs_per_cycle: int = 1) -> None:
        while True:
            processed = self.run_once(max_jobs=max_jobs_per_cycle)
            if processed == 0:
                time.sleep(self._poll_interval_seconds)

    def _process_job(self, job: dict[str, Any]) -> None:
        user_id = str(job.get("user_id") or "")
        job_id = str(job.get("id") or "")
        payload = dict(job.get("payload") or {})
        document_id = str(payload.get("document_id") or "")

        if not user_id or not job_id:
            return

        try:
            run_result = self._pipeline.run(user_id=user_id, payload=payload, job_id=job_id)
            if document_id:
                self._repository.update_document(
                    user_id=user_id,
                    document_id=document_id,
                    updates={"status": "ready", "error_message": None},
                )
            self._repository.update_job(
                user_id=user_id,
                job_id=job_id,
                updates={"status": "completed", "result": run_result.get("output"), "error_message": None},
            )
        except Exception as exc:
            if document_id:
                self._repository.update_document(
                    user_id=user_id,
                    document_id=document_id,
                    updates={"status": "error", "error_message": str(exc)},
                )
            self._repository.update_job(
                user_id=user_id,
                job_id=job_id,
                updates={"status": "failed", "error_message": str(exc)},
            )


def build_worker() -> IngestionWorker:
    settings = get_settings()
    return IngestionWorker(repository=get_repository(), poll_interval_seconds=settings.worker_poll_interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run backend_v5 ingestion worker")
    parser.add_argument("--once", action="store_true", help="Process available jobs once and exit")
    parser.add_argument("--max-jobs", type=int, default=1, help="Maximum jobs to process per cycle")
    args = parser.parse_args()

    worker = build_worker()
    if args.once:
        processed = worker.run_once(max_jobs=max(args.max_jobs, 1))
        print(f"Processed {processed} job(s).")
        return

    worker.run_forever(max_jobs_per_cycle=max(args.max_jobs, 1))


if __name__ == "__main__":
    main()
