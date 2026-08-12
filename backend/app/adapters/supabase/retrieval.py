"""Hybrid retrieval adapter over Supabase RPC (dense + lexical + RRF)."""

from __future__ import annotations

from typing import Any

from app.ports.retrieval import (
    HybridRetrievalResult,
    RetrievalFilters,
    RetrievedChunk,
    VectorSearchPort,
)
from supabase import Client


def _row_to_chunk(
    row: dict[str, Any],
    *,
    dense_distance: float | None = None,
    lexical_rank: float | None = None,
    score: float | None = None,
) -> RetrievedChunk:
    return RetrievedChunk(
        id=str(row["id"]),
        document_id=str(row["document_id"]),
        subject_id=str(row["subject_id"]),
        chunk_index=int(row["chunk_index"]),
        content=str(row["content"]),
        chapter_name=row.get("chapter_name"),
        page_start=row.get("page_start"),
        page_end=row.get("page_end"),
        metadata=row.get("metadata") or {},
        dense_distance=dense_distance if dense_distance is not None else row.get("distance"),
        lexical_rank=lexical_rank if lexical_rank is not None else row.get("rank"),
        score=score,
    )


class SupabaseHybridRetrievalAdapter(VectorSearchPort):
    def __init__(
        self,
        client: Client,
        *,
        dense_top_k: int = 20,
        lexical_top_k: int = 20,
        final_top_k: int = 8,
        rrf_k: int = 60,
    ) -> None:
        self._client = client
        self._dense_top_k = dense_top_k
        self._lexical_top_k = lexical_top_k
        self._final_top_k = final_top_k
        self._rrf_k = rrf_k

    async def dense_search(
        self,
        *,
        query_embedding: list[float],
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> list[RetrievedChunk]:
        payload = {
            "query_embedding": query_embedding,
            "match_count": match_count,
            "filter_user_id": filters.user_id,
            "filter_subject_id": filters.subject_id,
            "filter_document_id": filters.document_id,
        }
        response = self._client.rpc("match_chunks_dense", payload).execute()
        rows = response.data or []
        return [_row_to_chunk(row, dense_distance=row.get("distance")) for row in rows]

    async def lexical_search(
        self,
        *,
        query_text: str,
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> list[RetrievedChunk]:
        payload = {
            "query_text": query_text,
            "match_count": match_count,
            "filter_user_id": filters.user_id,
            "filter_subject_id": filters.subject_id,
            "filter_document_id": filters.document_id,
        }
        response = self._client.rpc("match_chunks_lexical", payload).execute()
        rows = response.data or []
        return [_row_to_chunk(row, lexical_rank=row.get("rank")) for row in rows]

    async def hybrid_search(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> HybridRetrievalResult:
        final_k = match_count or self._final_top_k
        dense = await self.dense_search(
            query_embedding=query_embedding,
            filters=filters,
            match_count=self._dense_top_k,
        )
        lexical = await self.lexical_search(
            query_text=query_text,
            filters=filters,
            match_count=self._lexical_top_k,
        )

        dense_ids = [chunk.id for chunk in dense]
        lexical_ids = [chunk.id for chunk in lexical]
        by_id = {chunk.id: chunk for chunk in [*dense, *lexical]}

        scores: dict[str, float] = {}
        for rank, chunk_id in enumerate(dense_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (self._rrf_k + rank)
        for rank, chunk_id in enumerate(lexical_ids, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (self._rrf_k + rank)

        ranked_ids = sorted(scores.keys(), key=lambda item: scores[item], reverse=True)[:final_k]
        merged: list[RetrievedChunk] = []
        for chunk_id in ranked_ids:
            base = by_id[chunk_id]
            merged.append(
                RetrievedChunk(
                    id=base.id,
                    document_id=base.document_id,
                    subject_id=base.subject_id,
                    chunk_index=base.chunk_index,
                    content=base.content,
                    chapter_name=base.chapter_name,
                    page_start=base.page_start,
                    page_end=base.page_end,
                    metadata=base.metadata,
                    dense_distance=base.dense_distance,
                    lexical_rank=base.lexical_rank,
                    score=scores[chunk_id],
                )
            )

        return HybridRetrievalResult(chunks=merged, dense_ids=dense_ids, lexical_ids=lexical_ids)
