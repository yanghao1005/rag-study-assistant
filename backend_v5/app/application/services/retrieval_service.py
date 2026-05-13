from __future__ import annotations

import json
import math
import re
from collections import Counter
from typing import Any

from app.core.config import get_settings
from app.domain.ports.repositories import StudyRepository
from openai import OpenAI


class RetrievalService:
    def __init__(self, *, repository: StudyRepository) -> None:
        self._repository = repository
        settings = get_settings()
        self._embeddings_provider = settings.embeddings_provider
        self._embedding_model = settings.openai_embedding_model
        if settings.embeddings_provider == "openai" and settings.openai_api_key:
            self._embedding_client: OpenAI | None = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url or None,
            )
        else:
            self._embedding_client = None

    def retrieve(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str,
        query: str,
        limit: int,
        source_document_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._repository.list_chunks_for_scope(user_id=user_id, scope=scope, scope_id=scope_id, limit=max(limit * 3, 10))
        if source_document_ids:
            allowed_ids = {doc_id.strip() for doc_id in source_document_ids if doc_id and doc_id.strip()}
            if allowed_ids:
                rows = [row for row in rows if str(row.get("document_id") or "") in allowed_ids]
        query_embedding = self._embed_query(query)
        query_terms = self._tokenize(query)
        query_term_set = set(query_terms)

        tokenized_rows: list[list[str]] = [self._tokenize(str(row.get("content") or "")) for row in rows]
        doc_freq: Counter[str] = Counter()
        for tokens in tokenized_rows:
            doc_freq.update(set(tokens))

        avg_doc_len = sum(len(tokens) for tokens in tokenized_rows) / max(len(tokenized_rows), 1)
        bm25_k1 = 1.2
        bm25_b = 0.75

        scored: list[dict[str, Any]] = []
        for row, row_tokens in zip(rows, tokenized_rows):
            content = str(row.get("content") or "")
            lower = content.lower()

            term_freq = Counter(row_tokens)
            lexical_score = 0.0
            for term in query_term_set:
                tf = float(term_freq.get(term, 0))
                if tf <= 0:
                    continue
                df = float(doc_freq.get(term, 0))
                idf = math.log((len(rows) - df + 0.5) / (df + 0.5) + 1.0)
                denom = tf + bm25_k1 * (1.0 - bm25_b + bm25_b * (len(row_tokens) / max(avg_doc_len, 1.0)))
                lexical_score += idf * ((tf * (bm25_k1 + 1.0)) / max(denom, 1e-6))

            matched_terms = len({term for term in query_term_set if term in term_freq})
            coverage_score = (matched_terms / float(max(len(query_term_set), 1))) if query_term_set else 0.0
            phrase_boost = 1.0 if query.strip() and query.lower().strip() in lower else 0.0

            semantic_score = 0.0
            if query_embedding is not None:
                row_embedding = self._normalize_embedding(row.get("embedding"))
                if row_embedding is not None:
                    cosine = self._cosine_similarity(query_embedding, row_embedding)
                    semantic_score = max(0.0, min(1.0, (cosine + 1.0) / 2.0))

            if query_embedding is not None:
                score = (0.45 * lexical_score) + (0.35 * semantic_score) + (0.15 * coverage_score) + (0.05 * phrase_boost)
            else:
                score = (0.7 * lexical_score) + (0.2 * coverage_score) + (0.1 * phrase_boost)

            scored.append(
                {
                    "document_id": row.get("document_id"),
                    "content": content,
                    "score": score,
                    "lexical_score": lexical_score,
                    "semantic_score": semantic_score,
                    "coverage_score": coverage_score,
                    "document_type": (row.get("metadata") or {}).get("document_type", "pdf"),
                    "page": row.get("page"),
                    "chapter_name": row.get("chapter_name"),
                    "preview": content[:220],
                }
            )

        scored.sort(key=lambda item: item.get("score", 0.0), reverse=True)
        return scored[:limit]

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if len(token) > 1]

    def _embed_query(self, query: str) -> list[float] | None:
        query = query.strip()
        if not query:
            return None

        if self._embeddings_provider == "stub":
            return None
        if not self._embedding_client:
            return None

        try:
            response = self._embedding_client.embeddings.create(model=self._embedding_model, input=[query])
            embedding = getattr(response.data[0], "embedding", None)
            if not isinstance(embedding, list) or not embedding:
                return None
            return [float(value) for value in embedding]
        except Exception:
            return None

    def _normalize_embedding(self, value: Any) -> list[float] | None:
        if isinstance(value, list) and value:
            normalized: list[float] = []
            for item in value:
                if isinstance(item, (int, float)):
                    normalized.append(float(item))
                else:
                    return None
            return normalized if normalized else None

        if isinstance(value, str) and value.strip().startswith("["):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return None
            return self._normalize_embedding(parsed)

        return None

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        size = min(len(a), len(b))
        if size == 0:
            return 0.0

        a_values = a[:size]
        b_values = b[:size]
        dot = sum(x * y for x, y in zip(a_values, b_values))
        norm_a = math.sqrt(sum(x * x for x in a_values))
        norm_b = math.sqrt(sum(y * y for y in b_values))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
