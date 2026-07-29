"""LLM and embedding provider ports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass(frozen=True, slots=True)
class ChatCompletionMessage:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class GenerationResult:
    content: str
    model: str
    raw: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StructuredGenerationResult:
    data: dict[str, Any]
    model: str
    raw: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)


class EmbeddingPort(ABC):
    """Creates dense vector embeddings for text."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        ...


class LLMPort(ABC):
    """Text / structured generation via an LLM provider."""

    @abstractmethod
    async def complete(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        ...

    @abstractmethod
    async def complete_json(
        self,
        *,
        messages: list[ChatCompletionMessage],
        schema_name: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> StructuredGenerationResult:
        """Generate JSON constrained to an application schema."""
        ...

    @abstractmethod
    async def stream(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        ...
