from __future__ import annotations

import jwt
from fastapi.testclient import TestClient

from app import container
from app.core.config import get_settings
from app.main import create_app


def _build_client() -> tuple[TestClient, dict[str, str]]:
    get_settings.cache_clear()
    container.get_repository.cache_clear()
    container.get_pipeline_use_case.cache_clear()
    container.get_documents_use_case.cache_clear()
    container.get_jobs_use_case.cache_clear()
    container.get_generation_use_case.cache_clear()
    container.get_chat_use_case.cache_clear()

    app = create_app()
    client = TestClient(app)
    token = jwt.encode({"sub": "ops-user", "role": "authenticated"}, "ops-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers


def test_rate_limit_blocks_after_threshold(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "ops-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    monkeypatch.setenv("ENABLE_RATE_LIMIT", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "3")
    monkeypatch.setenv("RATE_LIMIT_EXEMPT_PATHS", "/api/health")

    client, headers = _build_client()

    summary = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "ops-subject",
            "title": "Ops Rate Limit Source",
            "content": "Rate limiting tests need grounded content for flashcard generation.",
        },
        headers=headers,
    )
    assert summary.status_code == 200
    document_id = summary.json()["document_id"]

    payload = {
        "scope": "document",
        "scope_id": document_id,
        "query": "ops request",
        "count": 1,
        "save": False,
    }
    first = client.post("/api/generate/flashcards", json=payload, headers=headers)
    second = client.post("/api/generate/flashcards", json=payload, headers=headers)
    third = client.post("/api/generate/flashcards", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert "Retry-After" in third.headers


def test_abuse_protection_rejects_large_request(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "ops-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    monkeypatch.setenv("ENABLE_ABUSE_PROTECTION", "true")
    monkeypatch.setenv("MAX_REQUEST_SIZE_BYTES", "120")

    client, headers = _build_client()

    response = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "ops-subject",
            "title": "A",
            "content": "x" * 1000,
        },
        headers=headers,
    )

    assert response.status_code == 413
    body = response.json()
    assert body["error"] == "payload_too_large"
