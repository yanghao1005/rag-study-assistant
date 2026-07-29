"""Hybrid vector / lexical retrieval port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    id: str
    document_id: str
    subject_id: str
    chunk_index: int
    content: str
    chapter_name: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    dense_distance: float | None = None
    lexical_rank: float | None = None
    score: float | None = None


@dataclass(frozen=True, slots=True)
class RetrievalFilters:
    user_id: str
    subject_id: str | None = None
    document_id: str | None = None


@dataclass(frozen=True, slots=True)
class HybridRetrievalResult:
    chunks: list[RetrievedChunk]
    dense_ids: list[str] = field(default_factory=list)
    lexical_ids: list[str] = field(default_factory=list)


class VectorSearchPort(ABC):
    """3-stage hybrid retrieval: dense + lexical + merge/rerank."""

    @abstractmethod
    async def dense_search(
        self,
        *,
        query_embedding: list[float],
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> list[RetrievedChunk]:
        ...

    @abstractmethod
    async def lexical_search(
        self,
        *,
        query_text: str,
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> list[RetrievedChunk]:
        ...

    @abstractmethod
    async def hybrid_search(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        filters: RetrievalFilters,
        match_count: int = 10,
    ) -> HybridRetrievalResult:
        """Dense + lexical retrieval merged via RRF (rerank optional in adapter)."""
        ...
