import uuid

import httpx
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.main import app


def _ensure_profile(client_db) -> str:
    profiles = client_db.table("profiles").select("id").limit(1).execute().data or []
    if profiles:
        return profiles[0]["id"]

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise SystemExit("No profiles found and missing SUPABASE_URL/SUPABASE_SERVICE_KEY to create test user.")

    email = f"e2e-{uuid.uuid4().hex[:10]}@example.com"
    password = f"E2e-{uuid.uuid4().hex}"

    response = httpx.post(
        f"{settings.supabase_url}/auth/v1/admin/users",
        headers={
            "apikey": settings.supabase_service_key,
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "Content-Type": "application/json",
        },
        json={"email": email, "password": password, "email_confirm": True},
        timeout=30,
    )

    if response.status_code >= 400:
        raise SystemExit(f"Failed creating test auth user: {response.status_code} {response.text}")

    user_id = response.json().get("id")
    if not user_id:
        raise SystemExit("Auth user creation succeeded but no id returned.")

    profiles = client_db.table("profiles").select("id").eq("id", user_id).limit(1).execute().data or []
    if profiles:
        return profiles[0]["id"]

    return user_id


def main() -> None:
    client_db = get_supabase_client()
    if client_db is None:
        raise SystemExit("No Supabase client configured")

    user_id = _ensure_profile(client_db)
    subject_id = str(uuid.uuid4())
    document_id = str(uuid.uuid4())

    client_db.table("subjects").insert(
        {
            "id": subject_id,
            "user_id": user_id,
            "name": f"E2E Subject {subject_id[:8]}",
        }
    ).execute()

    client_db.table("documents").insert(
        {
            "id": document_id,
            "user_id": user_id,
            "subject_id": subject_id,
            "document_type": "summary",
            "filename": "e2e-summary.txt",
            "status": "ready",
        }
    ).execute()

    api = TestClient(app)
    payload = {
        "document_id": document_id,
        "user_id": user_id,
        "subject_id": subject_id,
        "document_type": "summary",
        "document_text": "Chapter 1 Intro\fChapter 2 Details about retrieval and generation.",
        "from": "parse_document",
        "to": "store_vectors",
        "debug": True,
    }

    response = api.post("/api/pipeline/run", json=payload)
    print("pipeline_status", response.status_code)
    print("pipeline_body", response.json())

    if response.status_code == 200:
        gen_payload = {
            "scope": "document",
            "scope_id": document_id,
            "query": "chapter intro details",
            "count": 3,
            "debug": True,
        }
        gen_response = api.post("/api/generate/flashcards", json=gen_payload)
        print("flashcards_status", gen_response.status_code)
        print("flashcards_body", gen_response.json())


if __name__ == "__main__":
    main()
