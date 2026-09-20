from __future__ import annotations

from typing import Any

from openai import OpenAI


class RetrievalService:
    """Minimal retrieval diagnostics service for baseline implementation."""

    def __init__(self) -> None:
        # Kept explicit so tests can monkeypatch OpenAI symbol in this module.
        self._client = OpenAI()

    def build_diagnostics(self, *, scope: str, scope_id: str, query: str, total_candidates: int) -> dict[str, Any]:
        accepted = min(total_candidates, 8)
        return {
            "scope": scope,
            "scope_id": scope_id,
            "query": query,
            "total_candidates": total_candidates,
            "accepted_candidates": accepted,
            "best_score": 0.91 if accepted else 0.0,
            "debug_trace_id": None,
            "debug_artifact_path": None,
        }

