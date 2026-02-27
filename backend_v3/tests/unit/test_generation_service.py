from app.application.generation_service import GenerationService
from app.core.exceptions import AppError
from app.domain.generation import GenerateFlashcardsRequest, ScopeType


def test_insufficient_context_when_scores_below_threshold() -> None:
    service = GenerationService()
    service.repository.store_chunks(
        document_id="doc-threshold-1",
        user_id="user-threshold-1",
        chunks=[
            {
                "content": "TCP is a transport protocol",
                "metadata": {"subject_id": "subject-th-1", "document_type": "pdf", "page": 1},
            }
        ],
        embeddings=[[0.1] * 8],
    )

    payload = GenerateFlashcardsRequest(
        scope=ScopeType.SUBJECT,
        scope_id="subject-th-1",
        count=1,
        query="quantum entanglement",
    )

    try:
        service.generate_flashcards(payload)
        assert False, "Expected insufficient_context error"
    except AppError as exc:
        assert exc.error == "insufficient_context"


def test_llm_retry_once_then_success(monkeypatch) -> None:
    service = GenerationService()
    service.settings.openai_api_key = "fake-key"
    service.repository.store_chunks(
        document_id="doc-retry-1",
        user_id="user-retry-1",
        chunks=[
            {
                "content": "UDP is a transport protocol and TCP is also a transport protocol.",
                "metadata": {"subject_id": "subject-retry-1", "document_type": "summary", "page": None},
            }
        ],
        embeddings=[[0.2] * 8],
    )

    calls = {"count": 0}

    def _fake_call_llm(prompt: str, schema_name: str, schema: dict):
        calls["count"] += 1
        if calls["count"] == 1:
            return "not-json"
        return '[{"front":"What is UDP?","back":"A connectionless transport protocol."}]'

    monkeypatch.setattr(service, "_call_llm", _fake_call_llm)

    payload = GenerateFlashcardsRequest(
        scope=ScopeType.SUBJECT,
        scope_id="subject-retry-1",
        count=1,
        query="transport protocol",
    )
    response = service.generate_flashcards(payload)
    assert len(response.flashcards) == 1
    assert calls["count"] == 2
    assert response.diagnostics is not None
    assert response.diagnostics.accepted_candidates >= 1
    assert response.diagnostics.best_score >= 0.6


def test_flashcards_uses_persisted_summary_with_chunks() -> None:
    service = GenerationService()
    service.settings.openai_api_key = ""
    service.repository.store_chunks(
        document_id="doc-summary-mix-1",
        user_id="user-summary-mix-1",
        chunks=[
            {
                "content": "Chunk context about value proposition and channels.",
                "metadata": {
                    "subject_id": "subject-summary-mix-1",
                    "document_type": "pdf",
                    "page": 1,
                },
            }
        ],
        embeddings=[[0.4] * 8],
    )
    service.repository.persist_document_index(
        document_id="doc-summary-mix-1",
        user_id="user-summary-mix-1",
        index_payload={"synopsis": "General summary of the document."},
    )

    payload = GenerateFlashcardsRequest(
        scope=ScopeType.DOCUMENT,
        scope_id="doc-summary-mix-1",
        count=2,
        query="value proposition",
    )
    response = service.generate_flashcards(payload)

    assert len(response.flashcards) >= 1
    assert response.flashcards[0].front == "Document Summary"
    assert "General summary" in response.flashcards[0].back

    generated_rows = service.repository._generated_contents
    assert len(generated_rows) == 1
    assert generated_rows[0]["type"] == "flashcard"
    assert generated_rows[0]["scope"] == "document"
    assert generated_rows[0]["document_id"] == "doc-summary-mix-1"


def test_flashcards_respect_length_caps() -> None:
    service = GenerationService()
    service.settings.openai_api_key = ""
    service.repository.store_chunks(
        document_id="doc-len-1",
        user_id="user-len-1",
        chunks=[
            {
                "content": "This is a very long chunk intended to be truncated in fallback generation output.",
                "metadata": {"subject_id": "subject-len-1", "document_type": "pdf", "page": 1},
            }
        ],
        embeddings=[[0.3] * 8],
    )

    payload = GenerateFlashcardsRequest(
        scope=ScopeType.DOCUMENT,
        scope_id="doc-len-1",
        count=1,
        query="long chunk",
        front_max_chars=20,
        back_max_chars=40,
    )
    response = service.generate_flashcards(payload)

    assert len(response.flashcards[0].front) <= 20
    assert len(response.flashcards[0].back) <= 40
