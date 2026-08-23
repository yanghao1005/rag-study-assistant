"""Document upload and listing routes."""

from __future__ import annotations

from contextlib import suppress
from typing import Annotated
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
    subject_id: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
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


@router.post("/{document_id}/reindex", status_code=201)
async def reindex_document(
    document_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    document = await container.documents.get(user_id=user.id, document_id=document_id)
    if document is None:
        raise AppError(status_code=404, error="document_not_found", message="Document not found.")
    if document.status == DocumentStatus.PROCESSING:
        raise AppError(
            status_code=409,
            error="already_processing",
            message="El documento ya se está indexando.",
        )
    document.status = DocumentStatus.QUEUED
    document.error_message = None
    await container.documents.update(document)
    job = await container.jobs.create(
        Job(
            id=str(uuid4()),
            user_id=user.id,
            job_type=JobType.REINDEX_DOCUMENT,
            status=JobStatus.QUEUED,
            subject_id=document.subject_id,
            document_id=document.id,
            payload={"filename": document.filename, "retry": True},
        )
    )
    return {
        "document_id": document.id,
        "job_id": job.id,
        "status": document.status.value,
        "filename": document.filename,
    }


@router.get("/{document_id}/chunks/{chunk_id}")
async def get_chunk(
    document_id: str,
    chunk_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    chunk = await container.documents.get_chunk(
        user_id=user.id, document_id=document_id, chunk_id=chunk_id
    )
    if chunk is None:
        raise AppError(status_code=404, error="chunk_not_found", message="Chunk not found.")
    document = await container.documents.get(user_id=user.id, document_id=document_id)
    return {
        "id": chunk.id,
        "document_id": chunk.document_id,
        "filename": document.filename if document else None,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "chapter_name": chunk.chapter_name,
        "page_start": chunk.page_start,
        "page_end": chunk.page_end,
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
        with suppress(Exception):
            await container.storage.delete(path=document.storage_path)
    deleted = await container.documents.delete(user_id=user.id, document_id=document_id)
    return {"deleted": deleted}
