from datetime import datetime, timezone
from uuid import uuid4


class InMemoryVectorRepository:
    def __init__(self) -> None:
        self._generated: list[dict] = []
        self._chunks: list[dict] = []

    def save_chunks(self, *, document_id: str, chunks: list[dict], scope: str, scope_id: str, user_id: str) -> int:
        for chunk in chunks:
            self._chunks.append(
                {
                    "id": chunk.get("id") or str(uuid4()),
                    "user_id": user_id,
                    "document_id": document_id,
                    "scope": scope,
                    "scope_id": scope_id,
                    "content": chunk.get("content", ""),
                    "page": chunk.get("page"),
                    "chapter_name": chunk.get("chapter_name"),
                    "document_type": chunk.get("document_type") or "pdf",
                    "score": float(chunk.get("score") or 0.5),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        return len(chunks)

    def retrieve(self, *, scope: str, scope_id: str, query: str | None, limit: int) -> list[dict]:
        persisted = [item for item in self._chunks if item.get("scope") == scope and item.get("scope_id") == scope_id]
        if persisted:
            normalized_query = (query or "").strip().lower()
            if normalized_query:
                persisted = [item for item in persisted if normalized_query in str(item.get("content", "")).lower()]

            ranked = sorted(persisted, key=lambda item: float(item.get("score", 0.5)), reverse=True)
            return [
                {
                    "id": item.get("id"),
                    "score": float(item.get("score", 0.5)),
                    "page": item.get("page"),
                    "chapter_name": item.get("chapter_name"),
                    "preview": item.get("content"),
                    "document_type": item.get("document_type") or "pdf",
                }
                for item in ranked[:limit]
            ]

        # Seed deterministic pseudo-candidates while real vector storage is not wired yet.
        normalized_query = (query or "study").strip() or "study"
        candidates = [
            {
                "id": f"cand-{index + 1}",
                "score": max(0.2, 0.95 - (index * 0.08)),
                "page": index + 1,
                "chapter_name": f"Chapter {index + 1}",
                "preview": f"Key concept about {normalized_query} ({scope}:{scope_id})",
                "document_type": "pdf",
            }
            for index in range(max(1, limit))
        ]
        return candidates[:limit]

    def save_generated(self, payload: dict) -> None:
        record = {
            "id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        self._generated.append(record)

    def list_generated(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict]:
        filtered = [
            item
            for item in self._generated
            if item.get("user_id") == user_id and item.get("scope") == scope and item.get("scope_id") == scope_id
        ]
        return list(reversed(filtered))[:limit]
