"""Async job and pipeline stage entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.entities.enums import JobStatus, JobType, PipelineStage, StageRunStatus
from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class Job:
    id: str
    user_id: str
    job_type: JobType
    status: JobStatus = JobStatus.QUEUED
    subject_id: str | None = None
    document_id: str | None = None
    progress: float = 0.0
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.progress <= 100.0:
            raise ValidationError("Job progress must be between 0 and 100")

    def mark_running(self, *, now: datetime) -> None:
        self.status = JobStatus.RUNNING
        self.started_at = now
        self.error_message = None

    def mark_completed(self, *, now: datetime, result: dict[str, Any] | None = None) -> None:
        self.status = JobStatus.COMPLETED
        self.progress = 100.0
        self.finished_at = now
        self.result = result
        self.error_message = None

    def mark_failed(self, *, now: datetime, message: str) -> None:
        self.status = JobStatus.FAILED
        self.finished_at = now
        self.error_message = message


@dataclass(slots=True)
class PipelineStageRun:
    id: str
    job_id: str
    stage: PipelineStage
    status: StageRunStatus
    duration_ms: int = 0
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.duration_ms < 0:
            raise ValidationError("duration_ms must be >= 0")
