from functools import lru_cache
from typing import Any

from app.core.config import get_settings


class _PostgrestAdapter:
    def __init__(self, client: Any) -> None:
        self._client = client

    def table(self, name: str) -> Any:
        return self._client.from_(name)


def _create_postgrest_client(supabase_url: str, key: str) -> Any:
    from postgrest import SyncPostgrestClient

    client = SyncPostgrestClient(
        f"{supabase_url}/rest/v1",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    return _PostgrestAdapter(client)


@lru_cache(maxsize=1)
def get_supabase_client() -> Any | None:
    settings = get_settings()
    if not settings.supabase_url:
        return None

    try:
        from supabase import create_client
    except ImportError:
        return None

    if settings.supabase_service_key:
        try:
            return create_client(settings.supabase_url, settings.supabase_service_key)
        except Exception as exc:
            if settings.supabase_service_key.startswith("sb_secret_"):
                try:
                    return _create_postgrest_client(settings.supabase_url, settings.supabase_service_key)
                except Exception as postgrest_exc:
                    if not settings.supabase_allow_anon_fallback:
                        raise RuntimeError(
                            "SUPABASE_SERVICE_KEY uses sb_secret format but PostgREST fallback failed."
                        ) from postgrest_exc
            if not settings.supabase_allow_anon_fallback:
                raise RuntimeError(
                    "SUPABASE_SERVICE_KEY is present but invalid. "
                    "Fix the key or set SUPABASE_ALLOW_ANON_FALLBACK=true for non-RLS environments."
                ) from exc

    if settings.supabase_allow_anon_fallback and settings.supabase_key:
        try:
            return create_client(settings.supabase_url, settings.supabase_key)
        except Exception as exc:
            raise RuntimeError("SUPABASE_KEY is invalid.") from exc

    if settings.supabase_url and settings.supabase_key and not settings.supabase_service_key:
        if not settings.supabase_allow_anon_fallback:
            raise RuntimeError(
                "SUPABASE_URL is configured without SUPABASE_SERVICE_KEY. "
                "RLS-protected writes require service role access. "
                "Set SUPABASE_SERVICE_KEY or explicitly enable SUPABASE_ALLOW_ANON_FALLBACK=true."
            )

    return None
