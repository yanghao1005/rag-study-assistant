"""Debug pipeline endpoints (gated by ENABLE_DEBUG_ENDPOINTS)."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter

from app.core.errors import AppError
from app.domain.entities.enums import JobStatus, JobType, PipelineStage
from app.domain.entities.job import Job
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import PipelineDebugRequest

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/pipeline")
async def run_pipeline_range(
    body: PipelineDebugRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    if not container.settings.enable_debug_endpoints:
        raise AppError(status_code=404, error="not_found", message="Debug endpoints disabled.")
    try:
        from_stage = PipelineStage(body.from_stage)
        to_stage = PipelineStage(body.to_stage)
    except ValueError as exc:
        raise AppError(
            status_code=400,
            error="invalid_stage",
            message="Unknown pipeline stage.",
        ) from exc

    document = await container.documents.get(user_id=user.id, document_id=body.document_id)
    if document is None:
        raise AppError(status_code=404, error="document_not_found", message="Document not found.")

    job = await container.jobs.create(
        Job(
            id=str(uuid4()),
            user_id=user.id,
            job_type=JobType.REINDEX_DOCUMENT,
            status=JobStatus.QUEUED,
            subject_id=document.subject_id,
            document_id=document.id,
            payload={"from_stage": from_stage.value, "to_stage": to_stage.value, "debug": True},
        )
    )
    completed = await container.ingestion_pipeline.run_range(
        job, from_stage=from_stage, to_stage=to_stage
    )
    stages = await container.jobs.list_stage_runs(completed.id)
    return {
        "job_id": completed.id,
        "status": completed.status.value,
        "result": completed.result,
        "stages": [
            {
                "stage": item.stage.value,
                "status": item.status.value,
                "duration_ms": item.duration_ms,
                "details": item.details,
            }
            for item in stages
        ],
    }
