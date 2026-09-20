"""Job status polling routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import AppError
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    job = await container.jobs.get(user_id=user.id, job_id=job_id)
    if job is None:
        raise AppError(status_code=404, error="job_not_found", message="Job not found.")
    stages = await container.jobs.list_stage_runs(job_id)
    return {
        "id": job.id,
        "job_type": job.job_type.value,
        "status": job.status.value,
        "progress": job.progress,
        "document_id": job.document_id,
        "subject_id": job.subject_id,
        "error_message": job.error_message,
        "result": job.result,
        "stages": [
            {
                "stage": s.stage.value,
                "status": s.status.value,
                "duration_ms": s.duration_ms,
                "details": s.details,
            }
            for s in stages
        ],
    }
