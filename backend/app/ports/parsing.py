"""Document parsing port (PDF / text extraction)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ParsedPage:
    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    pages: list[ParsedPage]
    total_pages: int
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text.strip())


@dataclass(frozen=True, slots=True)
class TextChunk:
    """Intermediate chunk before persistence / embedding."""

    index: int
    content: str
    chapter_name: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    token_count: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class DocumentParserPort(ABC):
    """Extracts text from uploaded binary documents."""

    @abstractmethod
    async def parse(self, data: bytes, *, filename: str) -> ParsedDocument:
        ...


class ChunkerPort(ABC):
    """Splits parsed documents into semantic chunks."""

    @abstractmethod
    def chunk(self, document: ParsedDocument) -> list[TextChunk]:
        ...
