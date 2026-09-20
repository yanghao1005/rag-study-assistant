from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse, Response

from app.container import get_documents_use_case, get_repository
from app.core.auth import AuthUser
from app.core.errors import AppError
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.documents import (
    CreateSummaryRequest,
    DeleteDocumentResponse,
    DocumentListResponse,
    DocumentRecord,
    DocumentUploadResponse,
    UpdateDocumentRequest,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    subject_id: str | None = Query(default=None),
    user: AuthUser = Depends(get_current_user),
) -> DocumentListResponse:
    items = get_documents_use_case().list_documents(user_id=user.user_id, subject_id=subject_id)
    return DocumentListResponse(items=[DocumentRecord(**item) for item in items])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    user_id: str | None = Form(default=None),
    user: AuthUser = Depends(get_current_user),
) -> DocumentUploadResponse:
    _ = user_id
    filename = file.filename or "document.pdf"
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise AppError(error="invalid_file_type", message="Only .pdf, .txt, and .md are supported", status_code=422)
    document_type = "pdf" if suffix == ".pdf" else "summary"

    content = await file.read()
    if not content:
        raise AppError(error="empty_file", message="Uploaded file is empty", status_code=422)

    result = get_documents_use_case().upload_document(
        user_id=user.user_id,
        subject_id=subject_id,
        original_name=filename,
        content=content,
        document_type=document_type,
    )
    return DocumentUploadResponse(**result)


@router.post("/summary", response_model=DocumentUploadResponse)
def create_summary_document(
    request: CreateSummaryRequest,
    user: AuthUser = Depends(get_current_user),
) -> DocumentUploadResponse:
    result = get_documents_use_case().create_summary_document(
        user_id=user.user_id,
        subject_id=request.subject_id,
        title=request.title,
        content=request.content,
    )
    return DocumentUploadResponse(**result)


@router.patch("/{document_id}", response_model=DocumentRecord)
def rename_document(
    document_id: str,
    request: UpdateDocumentRequest,
    user: AuthUser = Depends(get_current_user),
) -> DocumentRecord:
    updated = get_documents_use_case().rename_document(
        user_id=user.user_id,
        document_id=document_id,
        filename=request.filename,
    )
    return DocumentRecord(**updated)


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(
    document_id: str,
    user: AuthUser = Depends(get_current_user),
) -> DeleteDocumentResponse:
    get_documents_use_case().delete_document(user_id=user.user_id, document_id=document_id)
    return DeleteDocumentResponse(document_id=document_id)


@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    user_id: str | None = None,
    user: AuthUser = Depends(get_current_user),
) -> Response:
    _ = user_id
    document = get_repository().get_document(user_id=user.user_id, document_id=document_id)
    if not document:
        raise AppError(error="document_not_found", message="Document not found", status_code=404)

    storage_path = str(document.get("storage_path") or document.get("file_path") or "")
    filename = str(document.get("filename") or "document")
    content_text = document.get("content_text")

    if storage_path and Path(storage_path).exists():
        media_type = mimetypes.guess_type(storage_path)[0] or "application/octet-stream"
        return FileResponse(path=storage_path, media_type=media_type, filename=filename)

    if content_text:
        name = filename if filename.lower().endswith(".txt") else f"{filename}.txt"
        return Response(
            content=str(content_text),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{name}"'},
        )

    raise AppError(error="file_not_available", message="Stored file is not available", status_code=404)
