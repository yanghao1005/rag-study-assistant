"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # General
    app_name: str = Field(default="RAG Study Assistant", alias="APP_NAME")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    debug: bool = Field(default=False, alias="DEBUG")

    # CORS
    cors_allow_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ALLOW_ORIGINS",
    )

    # Supabase
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_jwt_secret: str = Field(default="", alias="SUPABASE_JWT_SECRET")

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # Ingestion
    enable_async_ingestion: bool = Field(default=True, alias="ENABLE_ASYNC_INGESTION")
    worker_poll_interval_seconds: float = Field(default=1.0, alias="WORKER_POLL_INTERVAL_SECONDS")
    max_upload_size_bytes: int = Field(default=25_000_000, alias="MAX_UPLOAD_SIZE_BYTES")

    # Rate limiting
    enable_rate_limit: bool = Field(default=True, alias="ENABLE_RATE_LIMIT")
    rate_limit_requests_per_minute: int = Field(default=120, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")

    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
