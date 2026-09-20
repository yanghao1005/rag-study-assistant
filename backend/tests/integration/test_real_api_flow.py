"""Real end-to-end API flow against live Supabase + OpenAI."""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.container import AppContainer
from app.domain.entities.enums import DocumentStatus, JobStatus
from tests.integration.conftest import RealUserSession, sample_pdf_bytes

pytestmark = pytest.mark.integration


def test_health_real(real_client: TestClient) -> None:
    response = real_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unauthorized_real(real_client: TestClient) -> None:
    response = real_client.get("/api/subjects")
    assert response.status_code == 401


def test_full_rag_flow_real(
    real_client: TestClient,
    real_container: AppContainer,
    real_user: RealUserSession,
    auth_headers: dict[str, str],
) -> None:
    # 1) Subjects CRUD
    created = real_client.post(
        "/api/subjects",
        headers=auth_headers,
        json={"name": "Biologia Integracion", "description": "Real integration subject"},
    )
    assert created.status_code == 201, created.text
    subject = created.json()
    subject_id = subject["id"]
    assert subject["name"] == "Biologia Integracion"

    listed = real_client.get("/api/subjects", headers=auth_headers)
    assert listed.status_code == 200
    assert any(item["id"] == subject_id for item in listed.json()["items"])

    patched = real_client.patch(
        f"/api/subjects/{subject_id}",
        headers=auth_headers,
        json={"description": "Updated for integration"},
    )
    assert patched.status_code == 200
    assert patched.json()["description"] == "Updated for integration"

    # 2) Upload PDF -> job
    pdf_bytes = sample_pdf_bytes()
    upload = real_client.post(
        "/api/documents/upload",
        headers=auth_headers,
        data={"subject_id": subject_id},
        files={"file": ("photosynthesis.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    upload_body = upload.json()
    document_id = upload_body["document_id"]
    job_id = upload_body["job_id"]

    job_resp = real_client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert job_resp.status_code == 200
    assert job_resp.json()["status"] == JobStatus.QUEUED.value

    # 3) Run ingestion pipeline (OpenAI embeddings + Supabase store)
    job = asyncio.run(real_container.jobs.get(user_id=real_user.user_id, job_id=job_id))
    assert job is not None
    try:
        completed = asyncio.run(real_container.ingestion_pipeline.process_job(job))
    except Exception as exc:  # noqa: BLE001
        message = str(exc).lower()
        if "insufficient_quota" in message or "exceeded your current quota" in message:
            pytest.fail(
                "OpenAI quota exceeded (insufficient_quota). "
                "Supabase path works; add billing/credits to OPENAI_API_KEY and re-run."
            )
        raise
    assert completed.status == JobStatus.COMPLETED

    doc_resp = real_client.get(f"/api/documents/{document_id}", headers=auth_headers)
    assert doc_resp.status_code == 200
    assert doc_resp.json()["status"] == DocumentStatus.READY.value

    # 4) RAG chat (OpenAI embed + LLM + hybrid retrieval)
    chat = real_client.post(
        "/api/chat/ask",
        headers=auth_headers,
        json={
            "subject_id": subject_id,
            "question": "Que es la fotosintesis segun el documento?",
            "document_id": document_id,
            "save": True,
        },
    )
    assert chat.status_code == 200, chat.text
    chat_body = chat.json()
    assert chat_body["answer"]
    assert isinstance(chat_body.get("citations"), list)

    # 5) Generation flashcards + quiz
    flashcards = real_client.post(
        "/api/generate/flashcards",
        headers=auth_headers,
        json={
            "subject_id": subject_id,
            "document_id": document_id,
            "count": 2,
            "query": "fotosintesis",
            "save": True,
        },
    )
    assert flashcards.status_code == 200, flashcards.text
    fc_body = flashcards.json()
    assert fc_body["artifact_id"]
    assert len(fc_body["cards"]) >= 1

    artifact = real_client.get(
        f"/api/generate/artifacts/{fc_body['artifact_id']}",
        headers=auth_headers,
    )
    assert artifact.status_code == 200
    assert artifact.json()["artifact_type"] == "flashcard_deck"

    quiz = real_client.post(
        "/api/generate/quiz",
        headers=auth_headers,
        json={
            "subject_id": subject_id,
            "document_id": document_id,
            "count": 2,
            "query": "Calvin cycle",
            "difficulty": "easy",
            "save": True,
        },
    )
    assert quiz.status_code == 200, quiz.text
    qz_body = quiz.json()
    assert qz_body["artifact_id"]
    assert len(qz_body["questions"]) >= 1

    quiz_artifact = real_client.get(
        f"/api/generate/artifacts/{qz_body['artifact_id']}",
        headers=auth_headers,
    )
    assert quiz_artifact.status_code == 200
    assert quiz_artifact.json()["artifact_type"] == "quiz"

    # 6) Cleanup document + subject (auth user deleted in fixture teardown)
    deleted_doc = real_client.delete(f"/api/documents/{document_id}", headers=auth_headers)
    assert deleted_doc.status_code == 200

    deleted_subject = real_client.delete(f"/api/subjects/{subject_id}", headers=auth_headers)
    assert deleted_subject.status_code == 200
