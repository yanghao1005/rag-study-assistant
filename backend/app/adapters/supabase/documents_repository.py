"""Supabase document / chunk repository adapter (ingestion path)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.document import Document, DocumentChunk
from app.domain.entities.enums import DocumentStatus, DocumentType
from app.ports.repositories import DocumentRepositoryPort
from supabase import Client


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _document_from_row(row: dict[str, Any]) -> Document:
    return Document(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        subject_id=str(row["subject_id"]),
        filename=str(row["filename"]),
        document_type=DocumentType(row.get("document_type") or "pdf"),
        storage_path=row.get("storage_path"),
        mime_type=row.get("mime_type"),
        status=DocumentStatus(row.get("status") or "queued"),
        error_message=row.get("error_message"),
        total_pages=int(row.get("total_pages") or 0),
        file_size=int(row.get("file_size") or 0),
        checksum=row.get("checksum"),
        synopsis=row.get("synopsis"),
        metadata=row.get("metadata") or {},
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


class SupabaseDocumentRepository(DocumentRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create(self, document: Document) -> Document:
        payload = {
            "id": document.id,
            "user_id": document.user_id,
            "subject_id": document.subject_id,
            "document_type": document.document_type.value,
            "filename": document.filename,
            "storage_path": document.storage_path,
            "mime_type": document.mime_type,
            "status": document.status.value,
            "error_message": document.error_message,
            "total_pages": document.total_pages,
            "file_size": document.file_size,
            "checksum": document.checksum,
            "synopsis": document.synopsis,
            "metadata": document.metadata,
        }
        response = self._client.table("documents").insert(payload).execute()
        return _document_from_row(response.data[0])

    async def get(self, *, user_id: str, document_id: str) -> Document | None:
        response = (
            self._client.table("documents")
            .select("*")
            .eq("id", document_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _document_from_row(response.data[0])

    async def list_for_subject(self, *, user_id: str, subject_id: str) -> list[Document]:
        response = (
            self._client.table("documents")
            .select("*")
            .eq("user_id", user_id)
            .eq("subject_id", subject_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [_document_from_row(row) for row in response.data or []]

    async def update(self, document: Document) -> Document:
        payload = {
            "status": document.status.value,
            "error_message": document.error_message,
            "total_pages": document.total_pages,
            "file_size": document.file_size,
            "storage_path": document.storage_path,
            "mime_type": document.mime_type,
            "checksum": document.checksum,
            "synopsis": document.synopsis,
            "metadata": document.metadata,
        }
        response = (
            self._client.table("documents")
            .update(payload)
            .eq("id", document.id)
            .eq("user_id", document.user_id)
            .execute()
        )
        return _document_from_row(response.data[0])

    async def delete(self, *, user_id: str, document_id: str) -> bool:
        response = (
            self._client.table("documents")
            .delete()
            .eq("id", document_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    async def replace_chunks(
        self,
        *,
        user_id: str,
        document_id: str,
        subject_id: str,
        chunks: list[DocumentChunk],
    ) -> int:
        self._client.table("document_chunks").delete().eq("document_id", document_id).execute()
        if not chunks:
            return 0

        rows = []
        for chunk in chunks:
            rows.append(
                {
                    "id": chunk.id or str(uuid4()),
                    "user_id": user_id,
                    "subject_id": subject_id,
                    "document_id": document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "chapter_name": chunk.chapter_name,
                    "page_start": chunk.page_start,
                    "page_end": chunk.page_end,
                    "token_count": chunk.token_count,
                    "metadata": chunk.metadata,
                    "embedding": chunk.embedding,
                }
            )
        # Insert in batches to avoid payload limits
        batch_size = 100
        inserted = 0
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            response = self._client.table("document_chunks").insert(batch).execute()
            inserted += len(response.data or [])
        return inserted

    async def list_chunks(
        self,
        *,
        user_id: str,
        document_id: str | None = None,
        subject_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentChunk]:
        query = self._client.table("document_chunks").select("*").eq("user_id", user_id)
        if document_id:
            query = query.eq("document_id", document_id)
        if subject_id:
            query = query.eq("subject_id", subject_id)
        response = query.order("chunk_index").limit(limit).execute()
        chunks: list[DocumentChunk] = []
        for row in response.data or []:
            chunks.append(
                DocumentChunk(
                    id=str(row["id"]),
                    user_id=str(row["user_id"]),
                    subject_id=str(row["subject_id"]),
                    document_id=str(row["document_id"]),
                    chunk_index=int(row["chunk_index"]),
                    content=str(row["content"]),
                    chapter_name=row.get("chapter_name"),
                    page_start=row.get("page_start"),
                    page_end=row.get("page_end"),
                    token_count=row.get("token_count"),
                    metadata=row.get("metadata") or {},
                    embedding=row.get("embedding"),
                    created_at=_parse_dt(row.get("created_at")),
                )
            )
        return chunks

    async def get_chunk(
        self,
        *,
        user_id: str,
        document_id: str,
        chunk_id: str,
    ) -> DocumentChunk | None:
        response = (
            self._client.table("document_chunks")
            .select("*")
            .eq("user_id", user_id)
            .eq("document_id", document_id)
            .eq("id", chunk_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        row = response.data[0]
        return DocumentChunk(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            subject_id=str(row["subject_id"]),
            document_id=str(row["document_id"]),
            chunk_index=int(row["chunk_index"]),
            content=str(row["content"]),
            chapter_name=row.get("chapter_name"),
            page_start=row.get("page_start"),
            page_end=row.get("page_end"),
            token_count=row.get("token_count"),
            metadata=row.get("metadata") or {},
            embedding=row.get("embedding"),
            created_at=_parse_dt(row.get("created_at")),
        )
