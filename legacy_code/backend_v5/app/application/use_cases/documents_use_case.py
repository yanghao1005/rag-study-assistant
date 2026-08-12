from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.core.config import Settings
from app.core.errors import AppError
from app.infrastructure.memory_repository import InMemoryRepository


@dataclass
class DocumentsUseCase:
    repository: InMemoryRepository
    pipeline_use_case: PipelineUseCase
    settings: Settings

    def create_summary_document(self, *, user_id: str, subject_id: str, title: str, content: str) -> dict[str, Any]:
        if not subject_id.strip():
            raise AppError(status_code=422, error="validation_error", message="subject_id is required.")
        if not title.strip() or not content.strip():
            raise AppError(status_code=422, error="validation_error", message="title and content are required.")

        document = self.repository.create_summary_document(
            user_id=user_id,
            subject_id=subject_id,
            title=title,
            content=content,
        )

        if self.settings.enable_async_ingestion:
            job = self.repository.create_job(
                user_id=user_id,
                job_type="summary_ingestion",
                payload={"document_id": document["id"]},
            )
            return {
                "document_id": document["id"],
                "filename": document["filename"],
                "file_path": document["file_path"],
                "status": "queued",
                "job_id": job["id"],
            }

        self.pipeline_use_case.ingest_document(
            user_id=user_id,
            document_id=document["id"],
            job_id=None,
        )
        return {
            "document_id": document["id"],
            "filename": document["filename"],
            "file_path": document["file_path"],
            "status": "ready",
            "job_id": None,
        }

    def list_documents(self, *, user_id: str, subject_id: str | None) -> dict[str, list[dict[str, Any]]]:
        return {"items": self.repository.list_documents(user_id=user_id, subject_id=subject_id)}

    def rename_document(self, *, user_id: str, document_id: str, filename: str) -> dict[str, Any]:
        updated = self.repository.update_document(
            user_id=user_id,
            document_id=document_id,
            updates={"filename": filename},
        )
        if not updated:
            raise AppError(status_code=404, error="document_not_found", message="Document not found.")
        return updated

    def delete_document(self, *, user_id: str, document_id: str) -> dict[str, Any]:
        ok = self.repository.delete_document(user_id=user_id, document_id=document_id)
        if not ok:
            raise AppError(status_code=404, error="document_not_found", message="Document not found.")
        return {"ok": True, "document_id": document_id}

