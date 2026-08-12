from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.errors import AppError
from app.infrastructure.memory_repository import InMemoryRepository


@dataclass
class JobsUseCase:
    repository: InMemoryRepository

    def get_job(self, *, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.repository.get_job(user_id=user_id, job_id=job_id)
        if not job:
            raise AppError(status_code=404, error="job_not_found", message="Job not found.")
        return job

