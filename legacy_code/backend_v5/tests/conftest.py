from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

# Ensure imports like "from app.main import create_app" work when tests are run
# from the repository root.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeEmbeddingItem:
    def __init__(self, embedding: list[float]) -> None:
        self.embedding = embedding


class _FakeEmbeddingResponse:
    def __init__(self, embeddings: list[list[float]]) -> None:
        self.data = [_FakeEmbeddingItem(embedding) for embedding in embeddings]


class _FakeChatCompletions:
    def create(self, *, messages, **kwargs):  # type: ignore[no-untyped-def]
        _ = kwargs
        user_content = ""
        for message in messages:
            if message.get("role") == "user":
                user_content = str(message.get("content") or "")

        count_match = re.search(r"Create\s+(\d+)\s+quiz questions", user_content, flags=re.IGNORECASE)
        if count_match:
            count = max(1, int(count_match.group(1)))
            payload = {
                "questions": [
                    {
                        "question": f"Quiz question {idx + 1}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": idx % 4,
                        "explanation": f"Grounded explanation {idx + 1}.",
                        "source_rank": 1,
                    }
                    for idx in range(count)
                ]
            }
            return _FakeCompletion(json.dumps(payload))

        count_match = re.search(r"Create\s+(\d+)\s+flashcards", user_content, flags=re.IGNORECASE)
        if count_match:
            count = max(1, int(count_match.group(1)))
            payload = {
                "flashcards": [
                    {
                        "front": f"Flashcard front {idx + 1}",
                        "back": f"Flashcard back {idx + 1}",
                        "source_rank": 1,
                    }
                    for idx in range(count)
                ]
            }
            return _FakeCompletion(json.dumps(payload))

        payload = {
            "answer": "Grounded chat answer.",
            "confidence": 0.84,
            "source_ranks": [1],
        }
        return _FakeCompletion(json.dumps(payload))


class _FakeEmbeddings:
    def create(self, *, input, **kwargs):  # type: ignore[no-untyped-def]
        _ = kwargs
        inputs = input if isinstance(input, list) else [input]
        embeddings: list[list[float]] = []
        for text in inputs:
            token_count = len(str(text).split())
            seed = float(max(token_count, 1))
            embeddings.append([
                seed / 10.0,
                (seed + 1.0) / 10.0,
                (seed + 2.0) / 10.0,
                (seed + 3.0) / 10.0,
                (seed + 4.0) / 10.0,
                (seed + 5.0) / 10.0,
                (seed + 6.0) / 10.0,
                (seed + 7.0) / 10.0,
            ])
        return _FakeEmbeddingResponse(embeddings)


class _FakeOpenAIClient:
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        _ = args
        _ = kwargs
        self.chat = type("ChatNamespace", (), {"completions": _FakeChatCompletions()})()
        self.embeddings = _FakeEmbeddings()


@pytest.fixture(autouse=True)
def _mock_openai_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("app.application.use_cases.generation_use_case.OpenAI", _FakeOpenAIClient)
    monkeypatch.setattr("app.application.use_cases.chat_use_case.OpenAI", _FakeOpenAIClient)
    monkeypatch.setattr("app.application.use_cases.pipeline_use_case.OpenAI", _FakeOpenAIClient)
    monkeypatch.setattr("app.application.services.retrieval_service.OpenAI", _FakeOpenAIClient)
