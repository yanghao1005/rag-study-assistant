"""
AI services package
Provides flexible LLM and embedding providers
"""
from app.services.ai.factory import (
    get_llm,
    get_embedding_service,
    get_llm_instance,
    get_embedding_instance
)

__all__ = [
    "get_llm",
    "get_embedding_service", 
    "get_llm_instance",
    "get_embedding_instance"
]
