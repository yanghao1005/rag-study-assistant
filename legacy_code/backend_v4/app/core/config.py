from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="SmartStudy Backend v5")
    api_prefix: str = Field(default="/api")
    debug: bool = Field(default=False)

    enable_debug_endpoints: bool = Field(default=False)
    enable_hybrid_retrieval: bool = Field(default=True)
    enable_summary_index: bool = Field(default=True)
    enable_graph_rag: bool = Field(default=False)
    enable_agentic_rag: bool = Field(default=False)

    vector_repository_provider: Literal["memory", "supabase"] = Field(default="memory")
    llm_provider: Literal["stub", "openai"] = Field(default="openai")
    embeddings_provider: Literal["stub", "openai"] = Field(default="openai")

    supabase_url: str | None = Field(default=None)
    supabase_key: str | None = Field(default=None)
    supabase_service_key: str | None = Field(default=None)
    supabase_generated_table: str = Field(default="generated_content")
    supabase_chunks_table: str = Field(default="document_chunks")

    openai_api_key: str | None = Field(default=None)
    openai_base_url: str | None = Field(default=None)
    openai_llm_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    debug_artifacts_dir: str = Field(default="debug_artifacts")
    benchmark_reports_dir: str = Field(default="benchmark_reports")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
