"""Document upload and listing routes."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.core.errors import AppError
from app.domain.entities.document import Document
from app.domain.entities.enums import DocumentStatus, DocumentType, JobStatus, JobType
from app.domain.entities.job import Job
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def list_documents(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str,
) -> dict[str, object]:
    items = await container.documents.list_for_subject(user_id=user.id, subject_id=subject_id)
    return {
        "items": [
            {
                "id": d.id,
                "subject_id": d.subject_id,
                "filename": d.filename,
                "status": d.status.value,
                "total_pages": d.total_pages,
                "file_size": d.file_size,
                "error_message": d.error_message,
            }
            for d in items
        ]
    }


@router.post("/upload", status_code=201)
async def upload_document(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str = Form(...),
    file: UploadFile = File(...),
) -> dict[str, object]:
    subject = await container.subjects.get(user_id=user.id, subject_id=subject_id)
    if subject is None:
        raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")

    data = await file.read()
    if not data:
        raise AppError(status_code=400, error="empty_file", message="Uploaded file is empty.")
    if len(data) > container.settings.max_upload_size_bytes:
        raise AppError(status_code=413, error="file_too_large", message="File exceeds size limit.")

    filename = file.filename or "document.pdf"
    document_id = str(uuid4())
    storage_path = f"{user.id}/{subject_id}/{document_id}/{filename}"
    content_type = file.content_type or "application/pdf"

    await container.storage.upload(
        path=storage_path,
        data=data,
        content_type=content_type,
        upsert=True,
    )

    document = await container.documents.create(
        Document(
            id=document_id,
            user_id=user.id,
            subject_id=subject_id,
            filename=filename,
            document_type=DocumentType.PDF,
            storage_path=storage_path,
            mime_type=content_type,
            status=DocumentStatus.QUEUED,
            file_size=len(data),
        )
    )

    job = await container.jobs.create(
        Job(
            id=str(uuid4()),
            user_id=user.id,
            job_type=JobType.INGEST_DOCUMENT,
            status=JobStatus.QUEUED,
            subject_id=subject_id,
            document_id=document.id,
            payload={"filename": filename},
        )
    )

    return {
        "document_id": document.id,
        "job_id": job.id,
        "status": document.status.value,
        "filename": document.filename,
    }


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    document = await container.documents.get(user_id=user.id, document_id=document_id)
    if document is None:
        raise AppError(status_code=404, error="document_not_found", message="Document not found.")
    return {
        "id": document.id,
        "subject_id": document.subject_id,
        "filename": document.filename,
        "status": document.status.value,
        "total_pages": document.total_pages,
        "file_size": document.file_size,
        "error_message": document.error_message,
        "storage_path": document.storage_path,
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    document = await container.documents.get(user_id=user.id, document_id=document_id)
    if document is None:
        raise AppError(status_code=404, error="document_not_found", message="Document not found.")
    if document.storage_path:
        try:
            await container.storage.delete(path=document.storage_path)
        except Exception:  # noqa: BLE001
            pass
    deleted = await container.documents.delete(user_id=user.id, document_id=document_id)
    return {"deleted": deleted}
