"""OpenAI embedding adapter (text-embedding-3-small → 1536 dims)."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.ports.llm import EmbeddingPort


class OpenAIEmbeddingAdapter(EmbeddingPort):
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        # OpenAI API limits batch size; keep batches modest.
        batch_size = 64
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = await self._client.embeddings.create(
                model=self._model,
                input=batch,
                dimensions=self._dimensions,
            )
            ordered = sorted(response.data, key=lambda item: item.index)
            vectors.extend([list(item.embedding) for item in ordered])
        return vectors
