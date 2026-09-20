from __future__ import annotations

from fastapi import APIRouter, Depends

from app.container import get_jobs_use_case
from app.core.auth import AuthUser
from app.core.errors import AppError
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.jobs import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, user: AuthUser = Depends(get_current_user)) -> JobResponse:
    item = get_jobs_use_case().get_job(user_id=user.user_id, job_id=job_id)
    if not item:
        raise AppError(error="job_not_found", message="Job not found", status_code=404)
    return JobResponse(**item)
