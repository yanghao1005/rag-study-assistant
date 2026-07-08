from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SmartStudy Backend v3"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    supabase_allow_anon_fallback: bool = False

    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold_pdf: float = 0.7
    similarity_threshold_summary: float = 0.6

    debug_artifacts_dir: str = "./.debug_runs"
    uploads_dir: str = "./uploads"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
