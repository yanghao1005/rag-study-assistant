from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="RAG Study Assistant Backend v5")
    api_prefix: str = Field(default="/api")
    debug: bool = Field(default=False)
    cors_allow_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    )

    enable_agentic_rag: bool = Field(default=False)
    enable_hybrid_retrieval: bool = Field(default=True)
    enable_debug_endpoints: bool = Field(default=False)
    enable_async_ingestion: bool = Field(default=True)
    worker_poll_interval_seconds: float = Field(default=1.0)
    enable_rate_limit: bool = Field(default=True)
    rate_limit_requests_per_minute: int = Field(default=120)
    rate_limit_exempt_paths: str = Field(default="/api/health")
    enable_abuse_protection: bool = Field(default=True)
    max_request_size_bytes: int = Field(default=1_048_576)
    max_upload_size_bytes: int = Field(default=25_000_000)
    blocked_user_agents: str = Field(default="sqlmap,nikto,nmap,masscan")
    enable_telemetry: bool = Field(default=False)
    otel_service_name: str = Field(default="rag-study-assistant-backend-v5")
    otel_exporter_otlp_endpoint: str | None = Field(default=None)
    otel_exporter_otlp_insecure: bool = Field(default=True)
    otel_metrics_export_interval_ms: int = Field(default=60_000)

    llm_provider: Literal["stub", "openai"] = Field(default="openai")
    embeddings_provider: Literal["stub", "openai"] = Field(default="openai")
    vector_repository_provider: Literal["memory", "supabase"] = Field(default="supabase")

    openai_api_key: str | None = Field(default=None)
    openai_base_url: str | None = Field(default=None)
    openai_llm_model: str = Field(default="gpt-4.1-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    supabase_url: str | None = Field(default=None)
    supabase_anon_key: str | None = Field(default=None)
    supabase_service_key: str | None = Field(default=None)
    supabase_jwt_secret: str | None = Field(default=None)

    debug_artifacts_dir: str = Field(default="debug_artifacts")
    benchmark_reports_dir: str = Field(default="benchmark_reports")
    uploads_dir: str = Field(default="uploads")

    @field_validator("supabase_url")
    @classmethod
    def normalize_supabase_url(cls, value: str | None) -> str | None:
        if not value:
            return value
        cleaned = value.strip().rstrip("/")
        if cleaned.endswith("/rest/v1"):
            cleaned = cleaned[: -len("/rest/v1")]
        return cleaned


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
