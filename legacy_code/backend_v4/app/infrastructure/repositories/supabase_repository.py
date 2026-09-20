from __future__ import annotations

from typing import Any


class SupabaseVectorRepository:
    def __init__(
        self,
        *,
        url: str,
        key: str,
        generated_table: str = "generated_content",
        chunks_table: str = "document_chunks",
    ) -> None:
        try:
            from supabase import Client, create_client
        except ImportError as exc:
            raise RuntimeError("supabase-py is required for Supabase repository") from exc

        self._client: Client = create_client(url, key)
        self._generated_table = generated_table
        self._chunks_table = chunks_table

    def retrieve(self, *, scope: str, scope_id: str, query: str | None, limit: int) -> list[dict[str, Any]]:
        try:
            request = (
                self._client.table(self._chunks_table)
                .select("id,content,page,chapter_name,document_type,score")
                .eq("scope", scope)
                .eq("scope_id", scope_id)
                .limit(limit)
            )
            if query:
                request = request.ilike("content", f"%{query}%")

            response = request.execute()
            rows = response.data or []
            return [
                {
                    "id": row.get("id"),
                    "score": float(row.get("score") or 0.5),
                    "page": row.get("page"),
                    "chapter_name": row.get("chapter_name"),
                    "preview": row.get("content"),
                    "document_type": row.get("document_type") or "pdf",
                }
                for row in rows
            ]
        except Exception:
            return []

    def save_chunks(self, *, document_id: str, chunks: list[dict], scope: str, scope_id: str, user_id: str) -> int:
        rows = []
        for chunk in chunks:
            rows.append(
                {
                    "user_id": user_id,
                    "document_id": document_id,
                    "content": chunk.get("content", ""),
                    "embedding": chunk.get("embedding") or [],
                    "metadata": chunk.get("metadata") or {},
                    "scope": scope,
                    "scope_id": scope_id,
                    "page": chunk.get("page"),
                    "chapter_name": chunk.get("chapter_name"),
                    "document_type": chunk.get("document_type") or "pdf",
                    "score": float(chunk.get("score") or 0.5),
                }
            )
        if not rows:
            return 0
        try:
            self._client.table(self._chunks_table).insert(rows).execute()
            return len(rows)
        except Exception:
            return 0

    def save_generated(self, payload: dict[str, Any]) -> None:
        try:
            self._client.table(self._generated_table).insert(payload).execute()
        except Exception:
            return None

    def list_generated(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        try:
            response = (
                self._client.table(self._generated_table)
                .select("*")
                .eq("user_id", user_id)
                .eq("scope", scope)
                .eq("scope_id", scope_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception:
            return []