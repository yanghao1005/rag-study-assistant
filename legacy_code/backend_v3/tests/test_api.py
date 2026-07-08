from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pipeline_stage_range() -> None:
    payload = {
        "document_id": "doc-123",
        "document_text": "Chapter 1 Introduction\\fSection 1.1 Basics",
        "from": "parse_document",
        "to": "split_chunks",
    }
    response = client.post("/api/pipeline/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc-123"
    assert data["executed_stages"] == ["parse_document", "detect_chapters", "split_chunks"]


def test_generate_flashcards_from_subject_scope() -> None:
    ingest_payload = {
        "document_id": "doc-201",
        "user_id": "user-201",
        "subject_id": "subject-201",
        "document_type": "summary",
        "document_text": "Chapter 1: TCP and UDP are transport protocols used in computer networks.",
    }
    ingest_response = client.post("/api/pipeline/run", json=ingest_payload)
    assert ingest_response.status_code == 200

    generate_payload = {
        "scope": "subject",
        "scope_id": "subject-201",
        "count": 2,
        "query": "transport protocols",
    }
    response = client.post("/api/generate/flashcards", json=generate_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["flashcards"]) >= 1
    assert "front" in data["flashcards"][0]
    assert "back" in data["flashcards"][0]
    assert isinstance(data["sources"], list)
    assert data["diagnostics"]["scope"] == "subject"
    assert data["diagnostics"]["accepted_candidates"] >= 1
    assert isinstance(data["diagnostics"]["context_scores"], list)


def test_generate_quiz_from_document_scope() -> None:
    ingest_payload = {
        "document_id": "doc-301",
        "user_id": "user-301",
        "subject_id": "subject-301",
        "document_type": "summary",
        "document_text": "OSI model has seven layers including transport and network layers.",
    }
    ingest_response = client.post("/api/pipeline/run", json=ingest_payload)
    assert ingest_response.status_code == 200

    generate_payload = {
        "scope": "document",
        "scope_id": "doc-301",
        "count": 1,
        "difficulty": "easy",
        "query": "OSI layers",
    }
    response = client.post("/api/generate/quiz", json=generate_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["questions"]) == 1
    question = data["questions"][0]
    assert len(question["options"]) == 4
    assert 0 <= question["correct_answer"] <= 3
    assert data["diagnostics"]["scope"] == "document"
    assert data["diagnostics"]["accepted_candidates"] >= 1


def test_generate_flashcards_debug_returns_trace_header() -> None:
    ingest_payload = {
        "document_id": "doc-401",
        "user_id": "user-401",
        "subject_id": "subject-401",
        "document_type": "summary",
        "document_text": "TCP reliability includes acknowledgments and retransmissions.",
    }
    ingest_response = client.post("/api/pipeline/run", json=ingest_payload)
    assert ingest_response.status_code == 200

    generate_payload = {
        "scope": "subject",
        "scope_id": "subject-401",
        "count": 1,
        "query": "tcp reliability",
        "debug": True,
    }
    response = client.post("/api/generate/flashcards", json=generate_payload)
    assert response.status_code == 200
    assert response.headers.get("X-Debug-Trace")

    data = response.json()
    assert data["diagnostics"]["debug_trace_id"]
    assert data["diagnostics"]["debug_artifact_path"]


def test_generate_summary_returns_persisted_document_index() -> None:
    ingest_payload = {
        "document_id": "doc-summary-501",
        "user_id": "user-summary-501",
        "subject_id": "subject-summary-501",
        "document_type": "summary",
        "document_text": "Business model canvas helps define value proposition and customer segments.",
        "from": "parse_document",
        "to": "build_document_index",
    }
    ingest_response = client.post("/api/pipeline/run", json=ingest_payload)
    assert ingest_response.status_code == 200

    summary_payload = {
        "scope_id": "doc-summary-501",
        "user_id": "user-summary-501",
    }
    response = client.post("/api/generate/summary", json=summary_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scope"] == "summary"
    assert data["scope_id"] == "doc-summary-501"
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0
