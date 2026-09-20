from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._documents: dict[str, dict[str, Any]] = {}
        self._jobs: dict[str, dict[str, Any]] = {}
        self._stage_runs: dict[str, list[dict[str, Any]]] = {}
        self._generated: dict[str, dict[str, Any]] = {}

    def create_summary_document(self, *, user_id: str, subject_id: str, title: str, content: str) -> dict[str, Any]:
        with self._lock:
            doc_id = str(uuid4())
            now = _now_iso()
            document = {
                "id": doc_id,
                "user_id": user_id,
                "subject_id": subject_id,
                "document_type": "summary",
                "filename": title,
                "storage_path": None,
                "content_text": content,
                "status": "processing",
                "error_message": None,
                "total_pages": 0,
                "file_size": len(content.encode("utf-8")),
                "file_path": "",
                "created_at": now,
                "updated_at": now,
            }
            self._documents[doc_id] = document
            return deepcopy(document)

    def get_document(self, *, document_id: str) -> dict[str, Any] | None:
        with self._lock:
            document = self._documents.get(document_id)
            return deepcopy(document) if document else None

    def list_documents(self, *, user_id: str, subject_id: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            items = [
                deepcopy(document)
                for document in self._documents.values()
                if document["user_id"] == user_id and (subject_id is None or document["subject_id"] == subject_id)
            ]
            return sorted(items, key=lambda item: item["created_at"], reverse=True)

    def update_document(self, *, user_id: str, document_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            document = self._documents.get(document_id)
            if not document or document["user_id"] != user_id:
                return None
            document.update(updates)
            document["updated_at"] = _now_iso()
            return deepcopy(document)

    def delete_document(self, *, user_id: str, document_id: str) -> bool:
        with self._lock:
            document = self._documents.get(document_id)
            if not document or document["user_id"] != user_id:
                return False
            del self._documents[document_id]
            return True

    def create_job(self, *, user_id: str, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            job_id = str(uuid4())
            now = _now_iso()
            job = {
                "id": job_id,
                "user_id": user_id,
                "job_type": job_type,
                "status": "queued",
                "payload": deepcopy(payload),
                "result": None,
                "error_message": None,
                "created_at": now,
                "updated_at": now,
            }
            self._jobs[job_id] = job
            self._stage_runs[job_id] = []
            return deepcopy(job)

    def list_queued_jobs(self, *, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            queued = [deepcopy(job) for job in self._jobs.values() if job["status"] == "queued"]
            queued.sort(key=lambda item: item["created_at"])
            return queued[:limit]

    def update_job(
        self,
        *,
        job_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            job["status"] = status
            job["result"] = deepcopy(result) if result is not None else job["result"]
            job["error_message"] = error_message
            job["updated_at"] = _now_iso()
            return deepcopy(job)

    def get_job(self, *, user_id: str, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["user_id"] != user_id:
                return None
            payload = deepcopy(job)
            payload["stage_runs"] = deepcopy(self._stage_runs.get(job_id, []))
            return payload

    def add_stage_run(
        self,
        *,
        job_id: str,
        stage: str,
        status: str,
        duration_ms: int = 0,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            run = {
                "id": str(uuid4()),
                "stage": stage,
                "status": status,
                "duration_ms": duration_ms,
                "details": deepcopy(details) if details else {},
                "created_at": _now_iso(),
            }
            self._stage_runs.setdefault(job_id, []).append(run)
            return deepcopy(run)

    def create_generated_item(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str,
        content_type: str,
        content_json: dict[str, Any],
    ) -> dict[str, Any]:
        with self._lock:
            item_id = str(uuid4())
            item = {
                "id": item_id,
                "user_id": user_id,
                "scope": scope,
                "scope_id": scope_id,
                "type": content_type,
                "content_json": deepcopy(content_json),
                "subject_id": scope_id if scope == "subject" else None,
                "document_id": scope_id if scope == "document" else None,
                "chapter_id": scope_id if scope == "chapter" else None,
                "created_at": _now_iso(),
            }
            self._generated[item_id] = item
            return deepcopy(item)

    def list_generated_items(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        with self._lock:
            items = [
                deepcopy(item)
                for item in self._generated.values()
                if item["user_id"] == user_id and item["scope"] == scope and item["scope_id"] == scope_id
            ]
            items.sort(key=lambda item: item["created_at"], reverse=True)
            return items[:limit]

    def get_generated_item(self, *, user_id: str, item_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._generated.get(item_id)
            if not item or item["user_id"] != user_id:
                return None
            return deepcopy(item)

    def update_generated_item(self, *, user_id: str, item_id: str, content_json: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            item = self._generated.get(item_id)
            if not item or item["user_id"] != user_id:
                return None
            item["content_json"] = deepcopy(content_json)
            return deepcopy(item)

    def delete_generated_item(self, *, user_id: str, item_id: str) -> bool:
        with self._lock:
            item = self._generated.get(item_id)
            if not item or item["user_id"] != user_id:
                return False
            del self._generated[item_id]
            return True

