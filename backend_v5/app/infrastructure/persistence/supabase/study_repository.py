from __future__ import annotations

from typing import Any

from postgrest.exceptions import APIError

from app.core.supabase_client import get_supabase_service_client


class SupabaseStudyRepository:
    def __init__(self) -> None:
        self._db = get_supabase_service_client()
        self._document_path_column = "storage_path"

    def _path_column_candidates(self) -> list[str]:
        primary = self._document_path_column
        return [primary] + [column for column in ("storage_path", "file_path") if column != primary]

    @staticmethod
    def _is_missing_documents_column(exc: APIError, column: str) -> bool:
        code = str(getattr(exc, "code", "") or "")
        message = str(getattr(exc, "message", "") or str(exc))
        return code == "PGRST204" and f"'{column}'" in message and "'documents'" in message

    @staticmethod
    def _vector_literal(vector: list[float]) -> str:
        return "[" + ",".join(f"{float(value):.10f}" for value in vector) + "]"

    def create_document(self, *, user_id: str, subject_id: str, document_type: str, filename: str, file_size: int, storage_path: str, content_text: str | None = None) -> dict[str, Any]:
        base_payload: dict[str, Any] = {
            "user_id": user_id,
            "subject_id": subject_id,
            "document_type": document_type,
            "filename": filename,
            "file_size": file_size,
            "status": "processing",
            "total_pages": 0,
        }
        if content_text is not None:
            base_payload["content_text"] = content_text

        last_missing_column_error: APIError | None = None
        for path_column in [*self._path_column_candidates(), None]:
            payload = dict(base_payload)
            if path_column is not None:
                payload[path_column] = storage_path
            try:
                result = self._db.table("documents").insert(payload).execute()
                row = (result.data or [{}])[0]
                if path_column is not None:
                    self._document_path_column = path_column
                row.setdefault("storage_path", row.get("storage_path") or row.get("file_path") or (storage_path if path_column is not None else ""))
                return row
            except APIError as exc:
                if path_column is not None and self._is_missing_documents_column(exc, path_column):
                    last_missing_column_error = exc
                    continue
                raise

        if last_missing_column_error is not None:
            raise last_missing_column_error

        raise RuntimeError("Failed to create document: no compatible path column found")

    def update_document(self, *, user_id: str, document_id: str, updates: dict[str, Any]) -> None:
        self._db.table("documents").update(updates).eq("id", document_id).eq("user_id", user_id).execute()

    def list_documents(self, *, user_id: str, subject_id: str | None = None) -> list[dict[str, Any]]:
        select_base = "id,user_id,subject_id,document_type,filename,status,error_message,total_pages,file_size,created_at,updated_at"

        last_missing_column_error: APIError | None = None
        for path_column in self._path_column_candidates():
            try:
                query = self._db.table("documents").select(f"{select_base},{path_column}").eq("user_id", user_id)
                if subject_id:
                    query = query.eq("subject_id", subject_id)
                result = query.order("created_at", desc=True).execute()
                rows = result.data or []
                normalized = []
                for row in rows:
                    row["storage_path"] = row.get("storage_path") or row.get("file_path") or ""
                    normalized.append(row)
                self._document_path_column = path_column
                return normalized
            except APIError as exc:
                if self._is_missing_documents_column(exc, path_column):
                    last_missing_column_error = exc
                    continue
                raise

        if last_missing_column_error is not None:
            raise last_missing_column_error
        return []

    def delete_document(self, *, user_id: str, document_id: str) -> bool:
        existing = self.get_document(user_id=user_id, document_id=document_id)
        if not existing:
            return False

        self._db.table("document_chunks").delete().eq("user_id", user_id).eq("document_id", document_id).execute()
        self._db.table("generated_content").delete().eq("user_id", user_id).eq("scope", "document").eq("scope_id", document_id).execute()
        self._db.table("documents").delete().eq("id", document_id).eq("user_id", user_id).execute()
        return True

    def get_document(self, *, user_id: str, document_id: str) -> dict[str, Any] | None:
        result = (
            self._db.table("documents")
            .select("*")
            .eq("id", document_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        data = result.data or []
        if not data:
            return None
        row = data[0]
        row.setdefault("storage_path", row.get("storage_path") or row.get("file_path") or "")
        return row

    def save_chunks(self, *, user_id: str, document_id: str, subject_id: str, chunks: list[dict[str, Any]]) -> int:
        if not chunks:
            return 0
        payload = []
        for idx, chunk in enumerate(chunks):
            row: dict[str, Any] = {
                "user_id": user_id,
                "document_id": document_id,
                "chunk_index": idx,
                "content": chunk.get("content", ""),
                "chapter_name": chunk.get("chapter_name"),
                "page": chunk.get("page"),
                "metadata": {
                    "subject_id": subject_id,
                    "document_type": chunk.get("document_type", "pdf"),
                    **(chunk.get("metadata") or {}),
                },
            }
            embedding = chunk.get("embedding")
            if isinstance(embedding, list) and embedding:
                row["embedding"] = self._vector_literal([float(value) for value in embedding])
            payload.append(
                row
            )
        self._db.table("document_chunks").insert(payload).execute()
        return len(payload)

    def list_chunks_for_scope(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        if scope in {"document", "summary"}:
            result = (
                self._db.table("document_chunks")
                .select("id,document_id,content,chapter_name,page,metadata,embedding")
                .eq("user_id", user_id)
                .eq("document_id", scope_id)
                .limit(limit)
                .execute()
            )
            return result.data or []

        if scope == "chapter":
            result = (
                self._db.table("document_chunks")
                .select("id,document_id,content,chapter_name,page,metadata,embedding")
                .eq("user_id", user_id)
                .eq("chapter_name", scope_id)
                .limit(limit)
                .execute()
            )
            return result.data or []

        if scope == "subject":
            docs = (
                self._db.table("documents")
                .select("id")
                .eq("user_id", user_id)
                .eq("subject_id", scope_id)
                .limit(100)
                .execute()
            )
            doc_ids = [row["id"] for row in (docs.data or []) if row.get("id")]
            collected: list[dict[str, Any]] = []
            for doc_id in doc_ids:
                if len(collected) >= limit:
                    break
                rows = (
                    self._db.table("document_chunks")
                    .select("id,document_id,content,chapter_name,page,metadata,embedding")
                    .eq("user_id", user_id)
                    .eq("document_id", doc_id)
                    .limit(max(limit - len(collected), 1))
                    .execute()
                )
                collected.extend(rows.data or [])
            return collected[:limit]

        return []

    def save_generated(self, *, user_id: str, scope: str, scope_id: str, content_type: str, content_json: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "user_id": user_id,
            "scope": scope,
            "scope_id": scope_id,
            "content_type": content_type,
            "content_json": content_json,
        }
        result = self._db.table("generated_content").insert(payload).execute()
        return (result.data or [{}])[0]

    def list_generated(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict[str, Any]]:
        result = (
            self._db.table("generated_content")
            .select("id,user_id,scope,scope_id,content_type,content_json,created_at")
            .eq("user_id", user_id)
            .eq("scope", scope)
            .eq("scope_id", scope_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def get_generated(self, *, user_id: str, generated_id: str) -> dict[str, Any] | None:
        result = (
            self._db.table("generated_content")
            .select("id,user_id,scope,scope_id,content_type,content_json,created_at")
            .eq("id", generated_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        return rows[0] if rows else None

    def update_generated(self, *, user_id: str, generated_id: str, content_json: dict[str, Any]) -> dict[str, Any] | None:
        result = (
            self._db.table("generated_content")
            .update({"content_json": content_json})
            .eq("id", generated_id)
            .eq("user_id", user_id)
            .execute()
        )
        rows = result.data or []
        return rows[0] if rows else None

    def delete_generated(self, *, user_id: str, generated_id: str) -> bool:
        existing = self.get_generated(user_id=user_id, generated_id=generated_id)
        if not existing:
            return False
        self._db.table("generated_content").delete().eq("id", generated_id).eq("user_id", user_id).execute()
        return True

    def create_job(self, *, user_id: str, job_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._db.table("jobs").insert({"user_id": user_id, "job_type": job_type, "payload": payload}).execute()
        return (result.data or [{}])[0]

    def claim_next_job(self, *, job_types: list[str] | None = None) -> dict[str, Any] | None:
        query = self._db.table("jobs").select("id,user_id,job_type,status,payload,result,error_message,created_at,updated_at").eq("status", "queued")
        if job_types:
            query = query.in_("job_type", job_types)

        queued = query.order("created_at").limit(1).execute()
        rows = queued.data or []
        if not rows:
            return None

        candidate = rows[0]
        claimed = (
            self._db.table("jobs")
            .update({"status": "running", "error_message": None})
            .eq("id", candidate["id"])
            .eq("status", "queued")
            .execute()
        )
        claimed_rows = claimed.data or []
        if not claimed_rows:
            return None
        return claimed_rows[0]

    def update_job(self, *, user_id: str, job_id: str, updates: dict[str, Any]) -> None:
        self._db.table("jobs").update(updates).eq("id", job_id).eq("user_id", user_id).execute()

    def add_stage_run(self, *, job_id: str, stage: str, status: str, duration_ms: int, details: dict[str, Any]) -> None:
        self._db.table("pipeline_stage_runs").insert(
            {
                "job_id": job_id,
                "stage": stage,
                "status": status,
                "duration_ms": duration_ms,
                "details": details,
            }
        ).execute()

    def get_job(self, *, user_id: str, job_id: str) -> dict[str, Any] | None:
        result = (
            self._db.table("jobs")
            .select("id,user_id,job_type,status,payload,result,error_message,created_at,updated_at")
            .eq("id", job_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        data = result.data or []
        return data[0] if data else None

    def list_stage_runs(self, *, job_id: str) -> list[dict[str, Any]]:
        result = (
            self._db.table("pipeline_stage_runs")
            .select("id,job_id,stage,status,duration_ms,details,created_at")
            .eq("job_id", job_id)
            .order("created_at")
            .execute()
        )
        return result.data or []
