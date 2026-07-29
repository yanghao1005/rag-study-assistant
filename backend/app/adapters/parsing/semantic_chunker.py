"""Structure-aware text chunker that prefers natural language boundaries.

Split priority (most semantic → least):
1. Section / chapter headings
2. Paragraphs
3. Sentences
4. Hard character cut (last resort)

Overlap prefers trailing complete sentences rather than raw character tails.
"""

from __future__ import annotations

import re

from app.ports.parsing import ChunkerPort, ParsedDocument, TextChunk

_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n+")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡0-9\"“«(])")
_HEADING_LINE = re.compile(
    r"""(?ix)^
    (?:
        (?:capítulo|capitulo|chapter|sección|seccion|section|tema|unit|unidad)\s+[\dIVXLCDM]+
        | \d+(?:\.\d+){0,3}\.?(?:\s+\S+)
        | [IVXLCDM]{1,6}\.\s+\S+
    )
    .{0,120}$
    """,
)


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(text) if p.strip()]
    return parts or [text]


def _is_heading(text: str) -> bool:
    compact = " ".join(text.strip().split())
    if not compact or len(compact) > 140:
        return False
    if "\n" in text.strip():
        return False
    return bool(_HEADING_LINE.match(compact))


def _overlap_tail(text: str, overlap_chars: int) -> str:
    """Return trailing overlap preferring complete sentence boundaries."""
    if overlap_chars <= 0 or not text:
        return ""
    if len(text) <= overlap_chars:
        return text

    window = text[-overlap_chars:]
    sentences = _split_sentences(window)
    if len(sentences) >= 2:
        # Keep the last 1–2 sentences that still fit the overlap budget.
        tail = sentences[-1]
        if len(sentences) >= 2 and len(sentences[-2]) + 1 + len(tail) <= overlap_chars:
            tail = f"{sentences[-2]} {tail}"
        return tail.strip()

    # Fall back to last whitespace-bounded fragment inside the window.
    space = window.find(" ")
    if space > 0 and space < len(window) - 1:
        return window[space + 1 :].strip()
    return window.strip()


def _hard_split(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            # Prefer breaking on whitespace inside the window.
            cut = text.rfind(" ", start + max(1, max_chars // 2), end)
            if cut > start:
                end = cut
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        next_start = end - overlap_chars if overlap_chars > 0 else end
        start = max(next_start, start + 1)
    return pieces


class SemanticChunkerAdapter(ChunkerPort):
    def __init__(self, *, max_chars: int = 1200, overlap_chars: int = 150) -> None:
        if max_chars <= 0:
            raise ValueError("max_chars must be > 0")
        if overlap_chars < 0 or overlap_chars >= max_chars:
            raise ValueError("overlap_chars must be >= 0 and < max_chars")
        self._max_chars = max_chars
        self._overlap_chars = overlap_chars

    def chunk(self, document: ParsedDocument) -> list[TextChunk]:
        units = self._extract_units(document)
        if not units:
            return []

        chunks: list[TextChunk] = []
        buffer = ""
        page_start: int | None = None
        page_end: int | None = None
        chapter_name: str | None = None

        def flush(*, force_chapter: str | None = None) -> None:
            nonlocal buffer, page_start, page_end, chapter_name
            content = buffer.strip()
            if not content:
                return
            active_chapter = force_chapter if force_chapter is not None else chapter_name
            chunks.append(
                TextChunk(
                    index=len(chunks),
                    content=content,
                    chapter_name=active_chapter,
                    page_start=page_start,
                    page_end=page_end,
                    token_count=max(len(content.split()), 1),
                    metadata={"split": "semantic"},
                )
            )
            buffer = _overlap_tail(content, self._overlap_chars)
            page_start = page_end
            # chapter stays until a new heading arrives

        for text, page_number, heading in units:
            if heading:
                if buffer.strip():
                    flush()
                chapter_name = " ".join(text.split())
                # Keep headings as their own small chunk when alone, or seed next buffer.
                if page_start is None:
                    page_start = page_number
                page_end = page_number
                candidate = text if not buffer else f"{buffer}\n\n{text}".strip()
                if len(candidate) <= self._max_chars:
                    buffer = candidate
                else:
                    flush()
                    buffer = text
                    page_start = page_number
                    page_end = page_number
                continue

            if page_start is None:
                page_start = page_number
            page_end = page_number

            candidate = f"{buffer}\n\n{text}".strip() if buffer else text
            if len(candidate) <= self._max_chars:
                buffer = candidate
                continue

            if buffer:
                flush()

            if len(text) <= self._max_chars:
                buffer = text
                page_start = page_number
                page_end = page_number
                continue

            # Oversized paragraph: split by sentences before hard cuts.
            for piece, split_kind in self._split_oversized(text):
                chunks.append(
                    TextChunk(
                        index=len(chunks),
                        content=piece,
                        chapter_name=chapter_name,
                        page_start=page_number,
                        page_end=page_number,
                        token_count=max(len(piece.split()), 1),
                        metadata={"split": split_kind},
                    )
                )
            buffer = _overlap_tail(chunks[-1].content, self._overlap_chars) if chunks else ""
            page_start = page_number if buffer else None
            page_end = page_number if buffer else None

        flush()
        return chunks

    def _extract_units(self, document: ParsedDocument) -> list[tuple[str, int, bool]]:
        units: list[tuple[str, int, bool]] = []
        for page in document.pages:
            if not page.text.strip():
                continue
            paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT.split(page.text) if p.strip()]
            if not paragraphs:
                paragraphs = [page.text.strip()]
            for paragraph in paragraphs:
                units.append((paragraph, page.page_number, _is_heading(paragraph)))
        return units

    def _split_oversized(self, text: str) -> list[tuple[str, str]]:
        sentences = _split_sentences(text)
        pieces: list[tuple[str, str]] = []
        buffer = ""

        def emit(content: str, kind: str) -> None:
            cleaned = content.strip()
            if cleaned:
                pieces.append((cleaned, kind))

        for sentence in sentences:
            if len(sentence) > self._max_chars:
                if buffer:
                    emit(buffer, "sentence")
                    buffer = ""
                for hard in _hard_split(sentence, self._max_chars, self._overlap_chars):
                    emit(hard, "hard")
                continue

            candidate = f"{buffer} {sentence}".strip() if buffer else sentence
            if len(candidate) <= self._max_chars:
                buffer = candidate
                continue

            if buffer:
                emit(buffer, "sentence")
            buffer = sentence

        if buffer:
            emit(buffer, "sentence")
        return pieces
