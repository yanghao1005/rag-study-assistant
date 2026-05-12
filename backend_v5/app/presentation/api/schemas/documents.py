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
