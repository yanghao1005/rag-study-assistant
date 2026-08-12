from __future__ import annotations

from pydantic import BaseModel, Field


class CreateSummaryRequest(BaseModel):
    subject_id: str = Field(min_length=1)
    user_id: str | None = None
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_path: str
    status: str
    job_id: str | None = None


class DocumentRecord(BaseModel):
    id: str
    subject_id: str
    document_type: str
    filename: str
    status: str
    error_message: str | None = None
    total_pages: int = 0
    file_size: int = 0
    file_path: str = ""
    created_at: str | None = None
    updated_at: str | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentRecord]


class UpdateDocumentRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)


class DeleteDocumentResponse(BaseModel):
    ok: bool = True
    document_id: str
