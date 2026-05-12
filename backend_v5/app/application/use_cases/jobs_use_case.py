from __future__ import annotations

from typing import Any

from app.domain.ports.repositories import StudyRepository


class JobsUseCase:
    def __init__(self, *, repository: StudyRepository) -> None:
        self._repository = repository

    def get_job(self, *, user_id: str, job_id: str) -> dict[str, Any] | None:
        job = self._repository.get_job(user_id=user_id, job_id=job_id)
        if not job:
            return None
        stages = self._repository.list_stage_runs(job_id=job_id)
        job["stage_runs"] = stages
        return job
