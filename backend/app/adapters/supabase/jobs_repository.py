"""Supabase jobs repository adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.entities.enums import JobStatus, JobType, PipelineStage, StageRunStatus
from app.domain.entities.job import Job, PipelineStageRun
from app.ports.repositories import JobRepositoryPort
from supabase import Client


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _job_from_row(row: dict[str, Any]) -> Job:
    return Job(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        job_type=JobType(row["job_type"]),
        status=JobStatus(row.get("status") or "queued"),
        subject_id=str(row["subject_id"]) if row.get("subject_id") else None,
        document_id=str(row["document_id"]) if row.get("document_id") else None,
        progress=float(row.get("progress") or 0),
        payload=row.get("payload") or {},
        result=row.get("result"),
        error_message=row.get("error_message"),
        started_at=_parse_dt(row.get("started_at")),
        finished_at=_parse_dt(row.get("finished_at")),
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


class SupabaseJobRepository(JobRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create(self, job: Job) -> Job:
        payload = {
            "id": job.id,
            "user_id": job.user_id,
            "subject_id": job.subject_id,
            "document_id": job.document_id,
            "job_type": job.job_type.value,
            "status": job.status.value,
            "progress": job.progress,
            "payload": job.payload,
            "result": job.result,
            "error_message": job.error_message,
        }
        response = self._client.table("jobs").insert(payload).execute()
        return _job_from_row(response.data[0])

    async def get(self, *, user_id: str, job_id: str) -> Job | None:
        response = (
            self._client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _job_from_row(response.data[0])

    async def update(self, job: Job) -> Job:
        payload = {
            "status": job.status.value,
            "progress": job.progress,
            "payload": job.payload,
            "result": job.result,
            "error_message": job.error_message,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "subject_id": job.subject_id,
            "document_id": job.document_id,
        }
        response = (
            self._client.table("jobs")
            .update(payload)
            .eq("id", job.id)
            .eq("user_id", job.user_id)
            .execute()
        )
        return _job_from_row(response.data[0])

    async def claim_next(self, *, job_types: list[str] | None = None) -> Job | None:
        # Service-role path: optimistic claim without requiring public RPC.
        # Prefer private.claim_next_job / public.claim_next_job when available
        # for multi-worker SKIP LOCKED semantics (see migration 0007).
        query = (
            self._client.table("jobs")
            .select("*")
            .eq("status", "queued")
            .order("created_at")
            .limit(1)
        )
        if job_types:
            query = query.in_("job_type", job_types)
        pending = query.execute()
        if not pending.data:
            return None

        row = pending.data[0]
        now = datetime.now().astimezone().isoformat()
        claimed = (
            self._client.table("jobs")
            .update(
                {
                    "status": "running",
                    "started_at": now,
                }
            )
            .eq("id", row["id"])
            .eq("status", "queued")
            .execute()
        )
        if not claimed.data:
            return None
        return _job_from_row(claimed.data[0])

    async def add_stage_run(self, stage_run: PipelineStageRun) -> PipelineStageRun:
        payload = {
            "id": stage_run.id,
            "job_id": stage_run.job_id,
            "stage": stage_run.stage.value,
            "status": stage_run.status.value,
            "duration_ms": stage_run.duration_ms,
            "details": stage_run.details,
        }
        response = self._client.table("pipeline_stage_runs").insert(payload).execute()
        row = response.data[0]
        return PipelineStageRun(
            id=str(row["id"]),
            job_id=str(row["job_id"]),
            stage=PipelineStage(row["stage"]),
            status=StageRunStatus(row["status"]),
            duration_ms=int(row.get("duration_ms") or 0),
            details=row.get("details") or {},
            created_at=_parse_dt(row.get("created_at")),
        )

    async def list_stage_runs(self, job_id: str) -> list[PipelineStageRun]:
        response = (
            self._client.table("pipeline_stage_runs")
            .select("*")
            .eq("job_id", job_id)
            .order("created_at")
            .execute()
        )
        runs: list[PipelineStageRun] = []
        for row in response.data or []:
            runs.append(
                PipelineStageRun(
                    id=str(row["id"]),
                    job_id=str(row["job_id"]),
                    stage=PipelineStage(row["stage"]),
                    status=StageRunStatus(row["status"]),
                    duration_ms=int(row.get("duration_ms") or 0),
                    details=row.get("details") or {},
                    created_at=_parse_dt(row.get("created_at")),
                )
            )
        return runs
