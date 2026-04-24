from fastapi.testclient import TestClient

from app import container
from app.core.config import get_settings
from app.main import app


def test_generate_flashcards_contract_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/generate/flashcards",
        json={"scope": "subject", "scope_id": "sub-1", "count": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert "sources" in data
    assert "diagnostics" in data
    assert {"scope", "scope_id", "query", "total_candidates", "accepted_candidates", "best_score"}.issubset(
        set(data["diagnostics"].keys())
    )
    assert data["diagnostics"]["scope"] == "subject"
    assert data["diagnostics"]["scope_id"] == "sub-1"
    assert "best_score" in data["diagnostics"]


def test_generate_quiz_contract_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/generate/quiz",
        json={"scope": "subject", "scope_id": "sub-1", "count": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert "diagnostics" in data
    assert {"scope", "scope_id", "query", "total_candidates", "accepted_candidates", "best_score"}.issubset(
        set(data["diagnostics"].keys())
    )


def test_generate_history_returns_items(monkeypatch) -> None:
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    get_settings.cache_clear()
    container.get_vector_repository.cache_clear()
    container.get_generation_service.cache_clear()

    client = TestClient(app)
    client.post(
        "/api/generate/flashcards",
        json={"scope": "subject", "scope_id": "sub-history", "count": 1, "user_id": "user-1", "save": True},
    )
    response = client.get(
        "/api/generate/history",
        params={"user_id": "user-1", "scope": "subject", "scope_id": "sub-history", "limit": 8},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1

    get_settings.cache_clear()
    container.get_vector_repository.cache_clear()
    container.get_generation_service.cache_clear()


def test_pipeline_debug_endpoint_is_gated(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_DEBUG_ENDPOINTS", "false")
    get_settings.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/pipeline/run",
        json={"document_id": "doc-1", "file_path": "dummy.pdf"},
    )
    assert response.status_code == 403
    data = response.json()
    assert data["error"] == "debug_endpoint_disabled"
    assert "request_id" in data

    get_settings.cache_clear()
