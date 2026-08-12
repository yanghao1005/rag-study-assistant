"""LLM-based listwise reranker for hybrid retrieval candidates."""

from __future__ import annotations

import json
import re

from app.ports.llm import ChatCompletionMessage, LLMPort
from app.ports.retrieval import RetrievedChunk


async def llm_rerank_chunks(
    llm: LLMPort,
    *,
    query: str,
    chunks: list[RetrievedChunk],
    top_k: int,
) -> list[RetrievedChunk]:
    """Reorder chunks with an LLM; falls back to input order on failure."""
    if not chunks or top_k <= 0:
        return []
    if len(chunks) == 1:
        return chunks[:top_k]

    numbered = "\n\n".join(
        f"[{i}] {chunk.content[:500]}" for i, chunk in enumerate(chunks, start=1)
    )
    try:
        result = await llm.complete_json(
            messages=[
                ChatCompletionMessage(
                    role="system",
                    content=(
                        "You rerank study passages for a question. "
                        'Return JSON: {"order":[best_index,...]} using 1-based indices. '
                        "Include each index at most once."
                    ),
                ),
                ChatCompletionMessage(
                    role="user",
                    content=f"Question: {query}\n\nPassages:\n{numbered}",
                ),
            ],
            schema_name="rerank",
            temperature=0.0,
        )
        order_raw = result.data.get("order") or []
        order: list[int] = []
        if isinstance(order_raw, list):
            for item in order_raw:
                try:
                    idx = int(item)
                except (TypeError, ValueError):
                    continue
                if 1 <= idx <= len(chunks) and idx not in order:
                    order.append(idx)
        if not order:
            # Fallback: parse any integers from content-like dumps
            text = json.dumps(result.data)
            for match in re.findall(r"\d+", text):
                idx = int(match)
                if 1 <= idx <= len(chunks) and idx not in order:
                    order.append(idx)
        if not order:
            return chunks[:top_k]

        reranked = [chunks[i - 1] for i in order]
        seen = {c.id for c in reranked}
        for chunk in chunks:
            if chunk.id not in seen:
                reranked.append(chunk)
        return reranked[:top_k]
    except Exception:  # noqa: BLE001
        return chunks[:top_k]
