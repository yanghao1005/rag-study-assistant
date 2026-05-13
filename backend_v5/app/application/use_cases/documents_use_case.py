from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.domain.ports.repositories import StudyRepository
from app.core.errors import AppError


class DocumentsUseCase:
    def __init__(
        self,
        *,
        repository: StudyRepository,
        pipeline_use_case: PipelineUseCase,
        uploads_dir: str = "uploads",
        enable_async_ingestion: bool = True,
    ) -> None:
        self._repository = repository
        self._pipeline = pipeline_use_case
        self._uploads_dir = Path(uploads_dir)
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        self._enable_async_ingestion = enable_async_ingestion

    def upload_document(
        self,
        *,
        user_id: str,
        subject_id: str,
        original_name: str,
        content: bytes,
        document_type: str,
    ) -> dict[str, Any]:
        stored_name = f"{uuid4()}-{Path(original_name).name}"
        stored_path = self._uploads_dir / stored_name
        stored_path.write_bytes(content)

        document = self._repository.create_document(
            user_id=user_id,
            subject_id=subject_id,
            document_type=document_type,
            filename=original_name,
            file_size=len(content),
            storage_path=str(stored_path),
        )

        job = self._repository.create_job(
            user_id=user_id,
            job_type="ingest_document",
            payload={
                "document_id": document["id"],
                "subject_id": subject_id,
                "file_path": str(stored_path),
                "document_type": document_type,
                "from": "validate_input",
                "to": "build_summary_index",
                "debug": True,
            },
        )

        status = "queued"
        if not self._enable_async_ingestion:
            self._run_job_inline(user_id=user_id, job_id=str(job["id"]))
            status = "ready"

        return {
            "document_id": document["id"],
            "filename": original_name,
            "file_path": str(stored_path),
            "status": status,
            "job_id": job["id"],
        }

    def create_summary_document(self, *, user_id: str, subject_id: str, title: str, content: str) -> dict[str, Any]:
        stored_name = f"{uuid4()}-{title[:60].strip().replace(' ', '_') or 'summary'}.txt"
        stored_path = self._uploads_dir / stored_name
        stored_path.write_text(content, encoding="utf-8")

        document = self._repository.create_document(
            user_id=user_id,
            subject_id=subject_id,
            document_type="summary",
            filename=title,
            file_size=len(content.encode("utf-8")),
            storage_path=str(stored_path),
            content_text=content,
        )

        job = self._repository.create_job(
            user_id=user_id,
            job_type="ingest_summary",
            payload={
                "document_id": document["id"],
                "subject_id": subject_id,
                "file_path": str(stored_path),
                "document_type": "summary",
                "from": "validate_input",
                "to": "build_summary_index",
                "debug": True,
            },
        )

        status = "queued"
        if not self._enable_async_ingestion:
            self._run_job_inline(user_id=user_id, job_id=str(job["id"]))
            status = "ready"

        return {
            "document_id": document["id"],
            "filename": title,
            "file_path": str(stored_path),
            "status": status,
            "job_id": job["id"],
        }

    def list_documents(self, *, user_id: str, subject_id: str | None = None) -> list[dict[str, Any]]:
        rows = self._repository.list_documents(user_id=user_id, subject_id=subject_id)
        return [
            {
                "id": str(row.get("id") or ""),
                "subject_id": str(row.get("subject_id") or ""),
                "document_type": str(row.get("document_type") or ""),
                "filename": str(row.get("filename") or "Untitled"),
                "status": str(row.get("status") or "unknown"),
                "error_message": row.get("error_message"),
                "total_pages": int(row.get("total_pages") or 0),
                "file_size": int(row.get("file_size") or 0),
                "file_path": str(row.get("storage_path") or row.get("file_path") or ""),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            }
            for row in rows
        ]

    def rename_document(self, *, user_id: str, document_id: str, filename: str) -> dict[str, Any]:
        clean_name = filename.strip()
        if not clean_name:
            raise AppError(error="invalid_filename", message="Filename cannot be empty", status_code=422)

        document = self._repository.get_document(user_id=user_id, document_id=document_id)
        if not document:
            raise AppError(error="document_not_found", message="Document not found", status_code=404)

        self._repository.update_document(user_id=user_id, document_id=document_id, updates={"filename": clean_name})
        updated = self._repository.get_document(user_id=user_id, document_id=document_id)
        if not updated:
            raise AppError(error="document_not_found", message="Document not found", status_code=404)

        return {
            "id": str(updated.get("id") or ""),
            "subject_id": str(updated.get("subject_id") or ""),
            "document_type": str(updated.get("document_type") or ""),
            "filename": str(updated.get("filename") or clean_name),
            "status": str(updated.get("status") or "unknown"),
            "error_message": updated.get("error_message"),
            "total_pages": int(updated.get("total_pages") or 0),
            "file_size": int(updated.get("file_size") or 0),
            "file_path": str(updated.get("storage_path") or updated.get("file_path") or ""),
            "created_at": updated.get("created_at"),
            "updated_at": updated.get("updated_at"),
        }

    def delete_document(self, *, user_id: str, document_id: str) -> None:
        document = self._repository.get_document(user_id=user_id, document_id=document_id)
        if not document:
            raise AppError(error="document_not_found", message="Document not found", status_code=404)

        storage_path = str(document.get("storage_path") or document.get("file_path") or "")
        deleted = self._repository.delete_document(user_id=user_id, document_id=document_id)
        if not deleted:
            raise AppError(error="document_not_found", message="Document not found", status_code=404)

        if storage_path:
            path = Path(storage_path)
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)

    def _run_job_inline(self, *, user_id: str, job_id: str) -> None:
        job = self._repository.get_job(user_id=user_id, job_id=job_id)
        if not job:
            return

        payload = dict(job.get("payload") or {})
        document_id = str(payload.get("document_id") or "")

        try:
            self._repository.update_job(user_id=user_id, job_id=job_id, updates={"status": "running", "error_message": None})
            run_result = self._pipeline.run(user_id=user_id, payload=payload, job_id=job_id)
            if document_id:
                self._repository.update_document(user_id=user_id, document_id=document_id, updates={"status": "ready", "error_message": None})
            self._repository.update_job(
                user_id=user_id,
                job_id=job_id,
                updates={"status": "completed", "result": run_result.get("output"), "error_message": None},
            )
        except Exception as exc:
            if document_id:
                self._repository.update_document(
                    user_id=user_id,
                    document_id=document_id,
                    updates={"status": "error", "error_message": str(exc)},
                )
            self._repository.update_job(
                user_id=user_id,
                job_id=job_id,
                updates={"status": "failed", "error_message": str(exc)},
            )
            raise
