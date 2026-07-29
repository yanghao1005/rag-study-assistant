"""API contract tests for all Phase 5 endpoints."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.subject import Subject
from app.main import create_app
from tests.fakes import build_fake_container


@pytest.fixture()
def api() -> tuple[TestClient, object]:
    container = build_fake_container()
    app = create_app(settings=container.settings, container=container)
    with TestClient(app) as client:
        yield client, container


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_health(api: tuple[TestClient, object]) -> None:
    client, _ = api
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unauthorized_without_token(api: tuple[TestClient, object]) -> None:
    client, _ = api
    response = client.get("/api/subjects")
    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


def test_subjects_crud(api: tuple[TestClient, object]) -> None:
    client, _ = api
    created = client.post(
        "/api/subjects",
        headers=auth_headers(),
        json={"name": "Álgebra", "description": "curso"},
    )
    assert created.status_code == 201
    subject_id = created.json()["id"]

    listed = client.get("/api/subjects", headers=auth_headers())
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1

    got = client.get(f"/api/subjects/{subject_id}", headers=auth_headers())
    assert got.status_code == 200
    assert got.json()["name"] == "Álgebra"

    updated = client.patch(
        f"/api/subjects/{subject_id}",
        headers=auth_headers(),
        json={"name": "Álgebra Lineal"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Álgebra Lineal"

    deleted = client.delete(f"/api/subjects/{subject_id}", headers=auth_headers())
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True


def test_documents_upload_list_get_delete(api: tuple[TestClient, object]) -> None:
    client, container = api
    subject = Subject(id=str(uuid4()), user_id="user-1", name="Physics")
    container.subjects.items[subject.id] = subject

    upload = client.post(
        "/api/documents/upload",
        headers=auth_headers(),
        data={"subject_id": subject.id},
        files={"file": ("notes.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert upload.status_code == 201
    body = upload.json()
    document_id = body["document_id"]
    job_id = body["job_id"]
    assert body["status"] == "queued"

    listed = client.get(
        "/api/documents",
        headers=auth_headers(),
        params={"subject_id": subject.id},
    )
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == document_id

    got = client.get(f"/api/documents/{document_id}", headers=auth_headers())
    assert got.status_code == 200
    assert got.json()["filename"] == "notes.pdf"

    job = client.get(f"/api/jobs/{job_id}", headers=auth_headers())
    assert job.status_code == 200
    assert job.json()["status"] == "queued"
    assert job.json()["document_id"] == document_id

    deleted = client.delete(f"/api/documents/{document_id}", headers=auth_headers())
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True


def test_chat_ask(api: tuple[TestClient, object]) -> None:
    client, container = api
    subject = Subject(id=str(uuid4()), user_id="user-1", name="History")
    container.subjects.items[subject.id] = subject

    response = client.post(
        "/api/chat/ask",
        headers=auth_headers(),
        json={"subject_id": subject.id, "question": "Qué es esto?", "save": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert payload["citations"]
    assert payload["thread_id"]


def test_generate_flashcards_and_quiz(api: tuple[TestClient, object]) -> None:
    client, container = api
    subject = Subject(id=str(uuid4()), user_id="user-1", name="Biology")
    container.subjects.items[subject.id] = subject

    flashcards = client.post(
        "/api/generate/flashcards",
        headers=auth_headers(),
        json={"subject_id": subject.id, "count": 1, "save": True},
    )
    assert flashcards.status_code == 200
    fc = flashcards.json()
    assert fc["cards"]
    assert fc["artifact_id"]

    artifact = client.get(
        f"/api/generate/artifacts/{fc['artifact_id']}",
        headers=auth_headers(),
    )
    assert artifact.status_code == 200
    assert artifact.json()["artifact_type"] == "flashcard_deck"
    assert artifact.json()["cards"]

    quiz = client.post(
        "/api/generate/quiz",
        headers=auth_headers(),
        json={"subject_id": subject.id, "count": 1, "difficulty": "easy", "save": True},
    )
    assert quiz.status_code == 200
    qz = quiz.json()
    assert qz["questions"]
    assert qz["artifact_id"]

    quiz_artifact = client.get(
        f"/api/generate/artifacts/{qz['artifact_id']}",
        headers=auth_headers(),
    )
    assert quiz_artifact.status_code == 200
    assert quiz_artifact.json()["questions"]


def test_job_not_found(api: tuple[TestClient, object]) -> None:
    client, _ = api
    response = client.get("/api/jobs/missing", headers=auth_headers())
    assert response.status_code == 404
    assert response.json()["error"] == "job_not_found"
