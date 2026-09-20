from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: str
    user_id: str
    job_type: str
    status: str
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    stage_runs: list[dict[str, Any]] = []
