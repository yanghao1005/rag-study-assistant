from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    app_name: str = Field(default="RAG Study Assistant Backend v5", alias="APP_NAME")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    debug: bool = Field(default=False, alias="DEBUG")

    enable_async_ingestion: bool = Field(default=True, alias="ENABLE_ASYNC_INGESTION")
    worker_poll_interval_seconds: float = Field(default=1.0, alias="WORKER_POLL_INTERVAL_SECONDS")

    enable_rate_limit: bool = Field(default=True, alias="ENABLE_RATE_LIMIT")
    rate_limit_requests_per_minute: int = Field(default=120, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_exempt_paths: str = Field(default="/api/health", alias="RATE_LIMIT_EXEMPT_PATHS")

    enable_abuse_protection: bool = Field(default=True, alias="ENABLE_ABUSE_PROTECTION")
    max_request_size_bytes: int = Field(default=1_048_576, alias="MAX_REQUEST_SIZE_BYTES")
    max_upload_size_bytes: int = Field(default=25_000_000, alias="MAX_UPLOAD_SIZE_BYTES")

    cors_allow_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ALLOW_ORIGINS",
    )

    vector_repository_provider: str = Field(default="memory", alias="VECTOR_REPOSITORY_PROVIDER")
    supabase_jwt_secret: str = Field(default="", alias="SUPABASE_JWT_SECRET")

    def cors_origins(self) -> List[str]:
        return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]

    def rate_limit_exempt(self) -> set[str]:
        return {item.strip() for item in self.rate_limit_exempt_paths.split(",") if item.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

