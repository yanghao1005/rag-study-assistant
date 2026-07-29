"""Fixtures for real Supabase + OpenAI integration tests.

Enabled only when RUN_REAL_INTEGRATION=1 and credentials are present in backend/.env.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from dataclasses import dataclass
from io import BytesIO
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.container import AppContainer, build_container
from app.core.config import Settings
from app.main import create_app


def _credentials_ready(settings: Settings) -> bool:
    required = [
        settings.supabase_url,
        settings.supabase_anon_key,
        settings.supabase_service_role_key,
        settings.supabase_jwt_secret,
        settings.openai_api_key,
    ]
    return all(bool(value) and "your-" not in str(value).lower() for value in required)


def _url_project_ref(settings: Settings) -> str:
    host = (settings.supabase_url or "").split("//")[-1]
    return host.split(".")[0].strip()


def _assert_supabase_keys_match_url(settings: Settings) -> None:
    """Fail fast when SUPABASE_URL and API keys belong to different projects."""
    url_ref = _url_project_ref(settings)
    for label, key in (
        ("SUPABASE_ANON_KEY", settings.supabase_anon_key),
        ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
    ):
        try:
            claims = jwt.decode(key, options={"verify_signature": False})
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"{label} is not a JWT API key: {exc}")
        key_ref = str(claims.get("ref") or "")
        if url_ref and key_ref and key_ref != url_ref:
            pytest.fail(
                f"{label} is for project ref={key_ref} but SUPABASE_URL is ref={url_ref}. "
                "Update backend/.env so URL, anon, service_role and JWT secret are from the same project."
            )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: real Supabase/OpenAI tests (set RUN_REAL_INTEGRATION=1)",
    )


@pytest.fixture(scope="session")
def real_settings() -> Settings:
    if os.getenv("RUN_REAL_INTEGRATION", "").strip() != "1":
        pytest.skip("Set RUN_REAL_INTEGRATION=1 to run real integration tests")
    settings = Settings().model_copy(
        update={
            "enable_rate_limit": False,
            "enable_async_ingestion": False,
            "debug": True,
        }
    )
    if not _credentials_ready(settings):
        pytest.skip("Missing or placeholder Supabase/OpenAI credentials in .env")
    if settings.llm_provider != "openai" or settings.embedding_provider != "openai":
        pytest.skip("Real integration tests require LLM_PROVIDER=openai and EMBEDDING_PROVIDER=openai")
    _assert_supabase_keys_match_url(settings)
    return settings


@dataclass(slots=True)
class RealUserSession:
    user_id: str
    email: str
    access_token: str


@pytest.fixture(scope="session")
def real_user(real_settings: Settings) -> Iterator[RealUserSession]:
    from app.adapters.supabase.client import create_supabase_admin_client

    admin = create_supabase_admin_client(real_settings)
    email = f"integration-{uuid4().hex[:10]}@example.com"
    password = f"Test-{uuid4().hex}!"

    created = admin.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
        }
    )
    user = created.user
    if user is None or not user.id:
        pytest.fail("Failed to create Supabase auth user for integration tests")

    now = int(time.time())
    token = jwt.encode(
        {
            "sub": user.id,
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
            "iat": now,
            "exp": now + 3600,
        },
        real_settings.supabase_jwt_secret,
        algorithm="HS256",
    )

    session = RealUserSession(user_id=user.id, email=email, access_token=token)
    try:
        yield session
    finally:
        try:
            admin.auth.admin.delete_user(user.id)
        except Exception:  # noqa: BLE001
            pass


@pytest.fixture(scope="session")
def real_container(real_settings: Settings) -> AppContainer:
    return build_container(real_settings)


@pytest.fixture(scope="session")
def real_client(real_settings: Settings, real_container: AppContainer) -> Iterator[TestClient]:
    app = create_app(settings=real_settings, container=real_container)
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def auth_headers(real_user: RealUserSession) -> dict[str, str]:
    return {"Authorization": f"Bearer {real_user.access_token}"}


def sample_pdf_bytes() -> bytes:
    """Tiny PDF with extractable study text for RAG/generation."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=400, height=200)
    # pypdf blank pages have no text; write a minimal content stream manually
    from pypdf.generic import (
        DecodedStreamObject,
        DictionaryObject,
        NameObject,
    )

    content = DecodedStreamObject()
    content.set_data(
        b"BT /F1 12 Tf 40 140 Td (Photosynthesis converts light into chemical energy.) Tj "
        b"0 -20 Td (Chlorophyll absorbs blue and red wavelengths of light.) Tj "
        b"0 -20 Td (The Calvin cycle fixes carbon dioxide into glucose.) Tj ET"
    )
    page[NameObject("/Contents")] = content
    resources = DictionaryObject()
    font = DictionaryObject()
    font[NameObject("/Type")] = NameObject("/Font")
    font[NameObject("/Subtype")] = NameObject("/Type1")
    font[NameObject("/BaseFont")] = NameObject("/Helvetica")
    fonts = DictionaryObject()
    fonts[NameObject("/F1")] = font
    resources[NameObject("/Font")] = fonts
    page[NameObject("/Resources")] = resources

    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
