from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.errors import AppError


@lru_cache(maxsize=1)
def get_supabase_service_client() -> Client:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_key:
        raise AppError(
            error="supabase_not_configured",
            message="SUPABASE_URL and SUPABASE_SERVICE_KEY are required",
            status_code=503,
        )
    return create_client(settings.supabase_url, settings.supabase_service_key)
