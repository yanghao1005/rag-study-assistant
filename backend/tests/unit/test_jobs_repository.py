"""Unit tests for the Supabase job claim adapter."""

from __future__ import annotations

import asyncio
from typing import Any

from app.adapters.supabase.jobs_repository import SupabaseJobRepository
from app.domain.entities.enums import JobStatus, JobType

_JOB_ROW: dict[str, Any] = {
    "id": "job-1",
    "user_id": "u1",
    "job_type": "ingest_document",
    "status": "running",
    "subject_id": None,
    "document_id": "d1",
    "progress": 0,
    "payload": {},
    "result": None,
    "error_message": None,
    "started_at": "2026-09-20T10:00:00+00:00",
    "finished_at": None,
    "created_at": "2026-09-20T09:00:00+00:00",
    "updated_at": "2026-09-20T10:00:00+00:00",
}


class _RpcClient:
    def __init__(self, data: Any, error: Exception | None = None) -> None:
        self.data = data
        self.error = error
        self.rpc_calls: list[tuple[str, dict[str, Any]]] = []
        self.fallback_used = False

    def rpc(self, name: str, params: dict[str, Any]) -> Any:
        self.rpc_calls.append((name, params))
        if self.error is not None:
            raise self.error

        parent = self

        class _Query:
            def execute(self) -> Any:
                class _Resp:
                    data = parent.data

                return _Resp()

        return _Query()

    def table(self, _name: str) -> Any:
        self.fallback_used = True
        parent = self

        class _Query:
            def select(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def eq(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def order(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def limit(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def in_(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def update(self, *_args: Any, **_kwargs: Any) -> Any:
                return self

            def execute(self) -> Any:
                class _Resp:
                    data = [parent.data] if isinstance(parent.data, dict) else parent.data or []

                return _Resp()

        return _Query()


def test_claim_next_uses_public_rpc() -> None:
    client = _RpcClient([_JOB_ROW])
    repo = SupabaseJobRepository(client)  # type: ignore[arg-type]
    job = asyncio.run(repo.claim_next(job_types=["ingest_document"]))
    assert client.rpc_calls == [("claim_next_job", {"p_job_types": ["ingest_document"]})]
    assert job is not None
    assert job.id == "job-1"
    assert job.job_type == JobType.INGEST_DOCUMENT
    assert job.status == JobStatus.RUNNING
    assert client.fallback_used is False


def test_claim_next_falls_back_when_rpc_missing() -> None:
    client = _RpcClient(_JOB_ROW, error=RuntimeError("function not found"))
    repo = SupabaseJobRepository(client)  # type: ignore[arg-type]
    job = asyncio.run(repo.claim_next(job_types=["ingest_document"]))
    assert client.rpc_calls == [("claim_next_job", {"p_job_types": ["ingest_document"]})]
    assert client.fallback_used is True
    assert job is not None
    assert job.id == "job-1"
