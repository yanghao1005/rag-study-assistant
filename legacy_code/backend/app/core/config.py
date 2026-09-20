"""
Configuration management with flexible AI provider switching
"""
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class AIProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    ANTHROPIC = "anthropic"


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    supabase_url: str
    supabase_key: str
    supabase_service_key: Optional[str] = None
    
    # AI Provider Configuration
    ai_provider: AIProvider = AIProvider.OPENAI
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ollama_embedding_model: str = "nomic-embed-text"
    
    # HuggingFace
    huggingface_api_key: Optional[str] = None
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.1"
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Cohere
    cohere_api_key: Optional[str] = None
    cohere_model: str = "command"
    cohere_embedding_model: str = "embed-english-v3.0"
    
    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-haiku-20240307"
    
    # Gemini
    gemini_api_key: Optional[str] = None
    gemini_embedding_model: str = "models/text-embedding-004"
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7
    top_k: int = 5
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on selected provider"""
        configs = {
            AIProvider.OPENAI: {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "temperature": 0.7,
            },
            AIProvider.OLLAMA: {
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
            },
            AIProvider.HUGGINGFACE: {
                "api_key": self.huggingface_api_key,
                "model": self.huggingface_model,
            },
            AIProvider.COHERE: {
                "api_key": self.cohere_api_key,
                "model": self.cohere_model,
            },
            AIProvider.ANTHROPIC: {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            },
        }
        return configs[self.ai_provider]
    
    def get_embedding_config(self) -> dict:
        """Get embedding configuration based on selected provider"""
        configs = {
            EmbeddingProvider.OPENAI: {
                "api_key": self.openai_api_key,
                "model": self.openai_embedding_model,
            },
            EmbeddingProvider.OLLAMA: {
                "base_url": self.ollama_base_url,
                "model": self.ollama_embedding_model,
            },
            EmbeddingProvider.HUGGINGFACE: {
                "api_key": self.huggingface_api_key,
                "model": self.huggingface_embedding_model,
            },
            EmbeddingProvider.COHERE: {
                "api_key": self.cohere_api_key,
                "model": self.cohere_embedding_model,
            },
        }
        return configs[self.embedding_provider]


# Global settings instance
settings = Settings()
