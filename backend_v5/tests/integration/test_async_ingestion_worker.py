from __future__ import annotations

import jwt
from fastapi.testclient import TestClient

from app import container
from app.core.config import get_settings
from app.main import create_app
from app.workers.ingestion_worker import IngestionWorker


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


def test_async_summary_ingestion_then_quiz(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    monkeypatch.setenv("ENABLE_ASYNC_INGESTION", "true")

    client, headers = _build_client()

    upload = client.post(
        "/api/documents/summary",
        json={
            "subject_id": "sub-async",
            "title": "Async Chapter",
            "content": "Neural networks use layers, weights, and activation functions for pattern learning.",
        },
        headers=headers,
    )
    assert upload.status_code == 200
    upload_body = upload.json()
    assert upload_body["status"] == "queued"
    assert upload_body.get("job_id")

    worker = IngestionWorker(
        repository=container.get_repository(),
        pipeline_use_case=container.get_pipeline_use_case(),
        poll_interval_seconds=0.1,
    )
    processed = worker.run_once(max_jobs=5)
    assert processed >= 1

    job = client.get(f"/api/jobs/{upload_body['job_id']}", headers=headers)
    assert job.status_code == 200
    job_body = job.json()
    assert job_body["status"] == "completed"

    quiz = client.post(
        "/api/generate/quiz",
        json={
            "scope": "document",
            "scope_id": upload_body["document_id"],
            "query": "neural networks",
            "count": 2,
            "save": True,
        },
        headers=headers,
    )
    assert quiz.status_code == 200
    quiz_body = quiz.json()
    assert len(quiz_body["questions"]) == 2
