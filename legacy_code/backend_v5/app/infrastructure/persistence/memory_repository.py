from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any


class InMemoryStudyRepository:
    def __init__(self) -> None:
        self._documents: dict[str, dict[str, Any]] = {}
        self._chunks: list[dict[str, Any]] = []
        self._generated: list[dict[str, Any]] = []
        self._jobs: dict[str, dict[str, Any]] = {}
        self._stage_runs: list[dict[str, Any]] = []

    def _now(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def create_document(self, *, user_id: str, subject_id: str, document_type: str, filename: str, file_size: int, storage_path: str, content_text: str | None = None) -> dict[str, Any]:
        doc_id = str(uuid4())
        row = {
            "id": doc_id,
            "user_id": user_id,
            "subject_id": subject_id,
            "document_type": document_type,
            "filename": filename,
            "storage_path": storage_path,
            "content_text": content_text,
            "status": "processing",
            "error_message": None,
            "total_pages": 0,
            "file_size": file_size,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self._documents[doc_id] = row
        return row.copy()

    def update_document(self, *, user_id: str, document_id: str, updates: dict[str, Any]) -> None:
        row = self._documents.get(document_id)
        if not row or row["user_id"] != user_id:
            return
        row.update(updates)
        row["updated_at"] = self._now()

    def list_documents(self, *, user_id: str, subject_id: str | None = None) -> list[dict[str, Any]]:
        rows = [row.copy() for row in self._documents.values() if row.get("user_id") == user_id]
        if subject_id:
            rows = [row for row in rows if row.get("subject_id") == subject_id]
        rows.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return rows

    def delete_document(self, *, user_id: str, document_id: str) -> bool:
        row = self._documents.get(document_id)
        if not row or row.get("user_id") != user_id:
            return False

        self._chunks = [chunk for chunk in self._chunks if not (chunk.get("user_id") == user_id and chunk.get("document_id") == document_id)]
        self._generated = [
            item
            for item in self._generated
            if not (
                item.get("user_id") == user_id
                and item.get("scope") == "document"
                and item.get("scope_id") == document_id
            )
        ]
        self._jobs = {
            job_id: job
            for job_id, job in self._jobs.items()
            if not (
                job.get("user_id") == user_id
                and isinstance(job.get("payload"), dict)
                and str((job.get("payload") or {}).get("document_id") or "") == document_id
            )
        }
        del self._documents[document_id]
        return True

    def get_document(self, *, user_id: str, document_id: str) -> dict[str, Any] | None:
        row = self._documents.get(document_id)
        if not row or row["user_id"] != user_id:
            return None
        return row.copy()

    def save_chunks(self, *, user_id: str, document_id: str, subject_id: str, chunks: list[dict[str, Any]]) -> int:
        for idx, chunk in enumerate(chunks):
            self._chunks.append(
                {
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "document_id": document_id,
                    "chunk_index": idx,
                    "content": chunk.get("content", ""),
                    "chapter_name": chunk.get("chapter_name"),
                    "page": chunk.get("page"),
                    "metadata": {
                        "subject_id": subject_id,
                        "document_type": chunk.get("document_type", "pdf"),
                        **(chunk.get("metadata") or {}),
                    },
                    "embedding": chunk.get("embedding"),
                    "created_at": self._now(),
                }
            )
        return len(chunks)

    def list_chunks_for_scope(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        rows = [row for row in self._chunks if row.get("user_id") == user_id]
        if scope == "document" or scope == "summary":
            rows = [row for row in rows if row.get("document_id") == scope_id]
        elif scope == "subject":
            rows = [row for row in rows if (row.get("metadata") or {}).get("subject_id") == scope_id]
        elif scope == "chapter":
            rows = [row for row in rows if row.get("chapter_name") == scope_id]
        return rows[:limit]

    def save_generated(self, *, user_id: str, scope: str, scope_id: str, content_type: str, content_json: dict[str, Any]) -> dict[str, Any]:
        row = {
            "id": str(uuid4()),
            "user_id": user_id,
            "scope": scope,
            "scope_id": scope_id,
            "content_type": content_type,
            "content_json": content_json,
            "created_at": self._now(),
        }
        self._generated.append(row)
        return row.copy()

    def list_generated(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self._generated
            if row.get("user_id") == user_id and row.get("scope") == scope and row.get("scope_id") == scope_id
        ]
        rows.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        return rows[:limit]

    def get_generated(self, *, user_id: str, generated_id: str) -> dict[str, Any] | None:
        for row in self._generated:
            if row.get("id") == generated_id and row.get("user_id") == user_id:
                return row.copy()
        return None

    def update_generated(self, *, user_id: str, generated_id: str, content_json: dict[str, Any]) -> dict[str, Any] | None:
        for row in self._generated:
            if row.get("id") != generated_id or row.get("user_id") != user_id:
                continue
            row["content_json"] = content_json
            row["updated_at"] = self._now()
            return row.copy()
        return None

    def delete_generated(self, *, user_id: str, generated_id: str) -> bool:
        initial = len(self._generated)
        self._generated = [
            row for row in self._generated if not (row.get("id") == generated_id and row.get("user_id") == user_id)
        ]
        return len(self._generated) != initial

    def create_job(self, *, user_id: str, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        job_id = str(uuid4())
        row = {
            "id": job_id,
            "user_id": user_id,
            "job_type": job_type,
            "status": "queued",
            "payload": payload,
            "result": None,
            "error_message": None,
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        self._jobs[job_id] = row
        return row.copy()

    def claim_next_job(self, *, job_types: list[str] | None = None) -> dict[str, Any] | None:
        allowed = set(job_types or [])
        queued = [
            row
            for row in self._jobs.values()
            if row.get("status") == "queued" and (not allowed or row.get("job_type") in allowed)
        ]
        if not queued:
            return None

        queued.sort(key=lambda item: item.get("created_at", ""))
        job = queued[0]
        job["status"] = "running"
        job["updated_at"] = self._now()
        return job.copy()

    def update_job(self, *, user_id: str, job_id: str, updates: dict[str, Any]) -> None:
        row = self._jobs.get(job_id)
        if not row or row["user_id"] != user_id:
            return
        row.update(updates)
        row["updated_at"] = self._now()

    def add_stage_run(self, *, job_id: str, stage: str, status: str, duration_ms: int, details: dict[str, Any]) -> None:
        self._stage_runs.append(
            {
                "id": str(uuid4()),
                "job_id": job_id,
                "stage": stage,
                "status": status,
                "duration_ms": duration_ms,
                "details": details,
                "created_at": self._now(),
            }
        )

    def get_job(self, *, user_id: str, job_id: str) -> dict[str, Any] | None:
        row = self._jobs.get(job_id)
        if not row or row["user_id"] != user_id:
            return None
        return row.copy()

    def list_stage_runs(self, *, job_id: str) -> list[dict[str, Any]]:
        rows = [row for row in self._stage_runs if row.get("job_id") == job_id]
        rows.sort(key=lambda item: item.get("created_at", ""))
        return rows
