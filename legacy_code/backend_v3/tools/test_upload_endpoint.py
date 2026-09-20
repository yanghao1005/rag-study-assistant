import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.database import get_supabase_client
from app.main import app


def main() -> None:
    client_db = get_supabase_client()
    if client_db is None:
        raise SystemExit("No Supabase client configured")

    profiles = client_db.table("profiles").select("id").limit(1).execute().data or []
    if not profiles:
        raise SystemExit("No profile found")

    user_id = profiles[0]["id"]
    subject_id = str(uuid.uuid4())
    client_db.table("subjects").insert(
        {"id": subject_id, "user_id": user_id, "name": f"Upload API {subject_id[:8]}"}
    ).execute()

    pdf_path = Path("pdf_tests_documents/1_BMC_OBS.pdf")
    if not pdf_path.exists():
        raise SystemExit(f"Missing pdf: {pdf_path}")

    api = TestClient(app)
    with pdf_path.open("rb") as handle:
        response = api.post(
            "/api/documents/upload",
            data={"subject_id": subject_id, "user_id": user_id},
            files={"file": (pdf_path.name, handle, "application/pdf")},
        )

    print("status", response.status_code)
    print(response.json())


if __name__ == "__main__":
    main()
