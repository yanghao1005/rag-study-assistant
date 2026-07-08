from typing import Any, Dict, List, Protocol
from uuid import UUID


class VectorRepository(Protocol):
    def store_chunks(
        self,
        document_id: str,
        user_id: str | None,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> int:
        ...

    def retrieve(self, query: str, top_k: int, scope: str | None = None, scope_id: str | None = None) -> List[Dict[str, Any]]:
        ...

    def persist_document_index(
        self,
        document_id: str,
        user_id: str | None,
        index_payload: Dict[str, Any],
    ) -> None:
        ...

    def get_document_summary(self, document_id: str, user_id: str | None = None) -> str | None:
        ...

    def persist_generated_content(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        generated_type: str,
        content_json: Dict[str, Any],
    ) -> None:
        ...

    def get_generated_history(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        ...


class InMemoryVectorRepository:
    def __init__(self) -> None:
        self._rows: List[Dict[str, Any]] = []
        self._document_indexes: Dict[str, Dict[str, Any]] = {}
        self._generated_contents: List[Dict[str, Any]] = []

    def clear(self) -> None:
        self._rows.clear()
        self._document_indexes.clear()
        self._generated_contents.clear()

    def store_chunks(
        self,
        document_id: str,
        user_id: str | None,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> int:
        for chunk, embedding in zip(chunks, embeddings):
            self._rows.append(
                {
                    "document_id": document_id,
                    "user_id": user_id,
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "embedding": embedding,
                }
            )
        return len(chunks)

    def retrieve(self, query: str, top_k: int, scope: str | None = None, scope_id: str | None = None) -> List[Dict[str, Any]]:
        tokens = {token.lower() for token in query.split() if token.strip()}
        scored: List[tuple[float, Dict[str, Any]]] = []
        for row in self._rows:
            if scope == "subject" and scope_id and row["metadata"].get("subject_id") != scope_id:
                continue
            if scope in {"document", "summary"} and scope_id and row.get("document_id") != scope_id:
                continue
            if scope == "chapter" and scope_id:
                row_chapter_id = row["metadata"].get("chapter_id")
                row_chapter_name = row["metadata"].get("chapter_name")
                if row_chapter_id != scope_id and row_chapter_name != scope_id:
                    continue
            content = row["content"].lower()
            matches = sum(1 for token in tokens if token in content)
            score = matches / max(1, len(tokens))
            scored.append((score, {**row, "_score": score}))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:top_k]]

    def persist_document_index(
        self,
        document_id: str,
        user_id: str | None,
        index_payload: Dict[str, Any],
    ) -> None:
        self._document_indexes[document_id] = {
            "user_id": user_id,
            **index_payload,
        }

    def get_document_summary(self, document_id: str, user_id: str | None = None) -> str | None:
        payload = self._document_indexes.get(document_id)
        if not payload:
            return None
        stored_user_id = payload.get("user_id")
        if user_id and stored_user_id and stored_user_id != user_id:
            return None
        synopsis = payload.get("synopsis")
        return synopsis if isinstance(synopsis, str) and synopsis.strip() else None

    def persist_generated_content(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        generated_type: str,
        content_json: Dict[str, Any],
    ) -> None:
        row: Dict[str, Any] = {
            "id": f"mem-{len(self._generated_contents) + 1}",
            "user_id": user_id,
            "scope": scope,
            "type": generated_type,
            "content_json": content_json,
            "created_at": None,
            "subject_id": None,
            "document_id": None,
            "chapter_id": None,
        }
        if scope == "subject":
            row["subject_id"] = scope_id
        elif scope in {"document", "summary"}:
            row["document_id"] = scope_id
        elif scope == "chapter":
            row["chapter_id"] = scope_id
        self._generated_contents.append(row)

    def get_generated_history(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        filtered: List[Dict[str, Any]] = []
        for row in reversed(self._generated_contents):
            if row.get("user_id") != user_id:
                continue
            if row.get("scope") != scope:
                continue
            if scope == "subject" and row.get("subject_id") != scope_id:
                continue
            if scope in {"document", "summary"} and row.get("document_id") != scope_id:
                continue
            if scope == "chapter" and row.get("chapter_id") != scope_id:
                continue
            filtered.append(row)
            if len(filtered) >= limit:
                break
        return filtered


class SupabaseVectorRepository:
    def __init__(self, client: Any) -> None:
        self.client = client

    @staticmethod
    def _as_uuid_or_none(value: str | None) -> str | None:
        if not value:
            return None
        try:
            return str(UUID(value))
        except ValueError:
            return None

    def store_chunks(
        self,
        document_id: str,
        user_id: str | None,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> int:
        payload = []
        for chunk, embedding in zip(chunks, embeddings):
            metadata = chunk["metadata"]
            payload.append(
                {
                    "user_id": user_id,
                    "document_id": document_id,
                    "chapter_id": self._as_uuid_or_none(metadata.get("chapter_id")),
                    "content": chunk["content"],
                    "metadata": metadata,
                    "embedding": embedding,
                }
            )
        self.client.table("document_chunks").insert(payload).execute()
        return len(payload)

    def retrieve(self, query: str, top_k: int, scope: str | None = None, scope_id: str | None = None) -> List[Dict[str, Any]]:
        query_builder = self.client.table("document_chunks").select("user_id,document_id,content,metadata")
        if scope == "subject" and scope_id:
            query_builder = query_builder.contains("metadata", {"subject_id": scope_id})
        if scope == "chapter" and scope_id:
            query_builder = query_builder.contains("metadata", {"chapter_id": scope_id})
        if scope in {"document", "summary"} and scope_id:
            query_builder = query_builder.eq("document_id", scope_id)
        response = query_builder.limit(top_k).execute()
        return response.data or []

    def persist_document_index(
        self,
        document_id: str,
        user_id: str | None,
        index_payload: Dict[str, Any],
    ) -> None:
        synopsis = index_payload.get("synopsis", "")
        query_builder = self.client.table("documents").update({"content_text": synopsis}).eq("id", document_id)
        if user_id:
            query_builder = query_builder.eq("user_id", user_id)
        query_builder.execute()

    def get_document_summary(self, document_id: str, user_id: str | None = None) -> str | None:
        query_builder = self.client.table("documents").select("content_text").eq("id", document_id)
        if user_id:
            query_builder = query_builder.eq("user_id", user_id)
        response = query_builder.limit(1).execute()
        rows = response.data or []
        if not rows:
            return None
        summary = rows[0].get("content_text")
        return summary if isinstance(summary, str) and summary.strip() else None

    def persist_generated_content(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        generated_type: str,
        content_json: Dict[str, Any],
    ) -> None:
        payload: Dict[str, Any] = {
            "user_id": user_id,
            "scope": scope,
            "type": generated_type,
            "content_json": content_json,
            "subject_id": None,
            "document_id": None,
            "chapter_id": None,
        }
        if scope == "subject":
            payload["subject_id"] = scope_id
        elif scope in {"document", "summary"}:
            payload["document_id"] = scope_id
        elif scope == "chapter":
            payload["chapter_id"] = scope_id
        self.client.table("generated_content").insert(payload).execute()

    def get_generated_history(
        self,
        user_id: str,
        scope: str,
        scope_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        query_builder = (
            self.client.table("generated_content")
            .select("id,user_id,scope,type,content_json,created_at,subject_id,document_id,chapter_id")
            .eq("user_id", user_id)
            .eq("scope", scope)
        )
        if scope == "subject":
            query_builder = query_builder.eq("subject_id", scope_id)
        elif scope in {"document", "summary"}:
            query_builder = query_builder.eq("document_id", scope_id)
        elif scope == "chapter":
            query_builder = query_builder.eq("chapter_id", scope_id)

        response = query_builder.order("created_at", desc=True).limit(limit).execute()
        return response.data or []
