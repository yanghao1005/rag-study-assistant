"""Outbound ports (hexagonal adapters interfaces)."""

from app.ports.auth import AuthenticatedUser, AuthPort
from app.ports.llm import (
    ChatCompletionMessage,
    EmbeddingPort,
    GenerationResult,
    LLMPort,
    StructuredGenerationResult,
)
from app.ports.parsing import ChunkerPort, DocumentParserPort, ParsedDocument, ParsedPage, TextChunk
from app.ports.repositories import (
    ChatRepositoryPort,
    DocumentRepositoryPort,
    JobRepositoryPort,
    ProfileRepositoryPort,
    StudyRepositoryPort,
    SubjectRepositoryPort,
)
from app.ports.retrieval import (
    HybridRetrievalResult,
    RetrievalFilters,
    RetrievedChunk,
    VectorSearchPort,
)
from app.ports.storage import StoragePort, StoredObject

__all__ = [
    "AuthPort",
    "AuthenticatedUser",
    "ChatCompletionMessage",
    "ChatRepositoryPort",
    "ChunkerPort",
    "DocumentParserPort",
    "DocumentRepositoryPort",
    "EmbeddingPort",
    "GenerationResult",
    "HybridRetrievalResult",
    "JobRepositoryPort",
    "LLMPort",
    "ParsedDocument",
    "ParsedPage",
    "ProfileRepositoryPort",
    "RetrievedChunk",
    "RetrievalFilters",
    "StoragePort",
    "StoredObject",
    "StructuredGenerationResult",
    "StudyRepositoryPort",
    "SubjectRepositoryPort",
    "TextChunk",
    "VectorSearchPort",
]
