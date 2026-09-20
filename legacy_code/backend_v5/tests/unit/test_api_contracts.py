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
    token = jwt.encode({"sub": "user-1", "role": "authenticated"}, "test-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    return client, headers


def test_generate_flashcards_and_history(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    client, headers = _build_client()

    summary = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "sub-1",
            "title": "Flashcard Source",
            "content": "Neural networks learn representations through layers and optimization.",
        },
        headers=headers,
    )
    assert summary.status_code == 200
    document_id = summary.json()["document_id"]

    response = client.post(
        "/api/generate/flashcards",
        json={
            "scope": "document",
            "scope_id": document_id,
            "query": "neural network basics",
            "count": 3,
            "save": True,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "flashcards" in body
    assert len(body["flashcards"]) == 3

    history = client.get(
        "/api/generate/history",
        params={"scope": "document", "scope_id": document_id, "limit": 10},
        headers=headers,
    )
    assert history.status_code == 200
    history_body = history.json()
    assert "items" in history_body
    assert len(history_body["items"]) >= 1


def test_generate_history_rejects_invalid_document_scope_id(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    client, headers = _build_client()

    response = client.get(
        "/api/generate/history",
        params={"scope": "document", "scope_id": "undefined", "limit": 10},
        headers=headers,
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "invalid_scope_id"


def test_create_summary_document(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    client, headers = _build_client()

    response = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "sub-2",
            "title": "Chapter Overview",
            "content": "This is a summary text used for ingestion and indexing in tests.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body.get("document_id")


def test_protected_endpoint_requires_auth(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    client, _headers = _build_client()

    response = client.post(
        "/api/generate/flashcards",
        json={
            "scope": "subject",
            "scope_id": "sub-3",
            "query": "auth check",
            "count": 1,
        },
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"] == "unauthorized"


def test_pipeline_accepts_from_to_aliases(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "false")
    client, headers = _build_client()

    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("Chapter 1\nThis is pipeline alias coverage text.", encoding="utf-8")

    response = client.post(
        "/api/pipeline/run",
        json={
            "document_id": "doc-alias-1",
            "file_path": str(sample_file),
            "subject_id": "sub-alias",
            "from": "validate_input",
            "to": "semantic_chunking",
            "debug": False,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert "executed_stages" in body
    assert body["executed_stages"][0] == "validate_input"
    assert body["executed_stages"][-1] == "semantic_chunking"
