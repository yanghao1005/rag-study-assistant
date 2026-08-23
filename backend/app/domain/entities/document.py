"""Document and chunk entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.entities.enums import DocumentStatus, DocumentType
from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class Document:
    id: str
    user_id: str
    subject_id: str
    filename: str
    document_type: DocumentType = DocumentType.PDF
    storage_path: str | None = None
    mime_type: str | None = None
    status: DocumentStatus = DocumentStatus.QUEUED
    error_message: str | None = None
    total_pages: int = 0
    file_size: int = 0
    checksum: str | None = None
    synopsis: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING
        self.error_message = None

    def mark_ready(self, *, total_pages: int = 0) -> None:
        self.status = DocumentStatus.READY
        self.total_pages = max(total_pages, 0)
        self.error_message = None

    def mark_error(self, message: str) -> None:
        self.status = DocumentStatus.ERROR
        self.error_message = message


@dataclass(slots=True)
class DocumentChunk:
    id: str
    user_id: str
    subject_id: str
    document_id: str
    chunk_index: int
    content: str
    chapter_name: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    token_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValidationError("chunk_index must be >= 0")
        if not self.content.strip():
            raise ValidationError("chunk content cannot be empty")

    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None and len(self.embedding) > 0
