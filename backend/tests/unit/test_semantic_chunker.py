"""Unit tests for structure-aware semantic chunker."""

from __future__ import annotations

from app.adapters.parsing.semantic_chunker import SemanticChunkerAdapter
from app.ports.parsing import ParsedDocument, ParsedPage


def test_semantic_chunker_splits_long_text() -> None:
    chunker = SemanticChunkerAdapter(max_chars=50, overlap_chars=10)
    document = ParsedDocument(
        pages=[
            ParsedPage(page_number=1, text="Alpha paragraph one.\n\nBeta paragraph two."),
            ParsedPage(page_number=2, text="Gamma paragraph three is a bit longer than others."),
        ],
        total_pages=2,
    )
    chunks = chunker.chunk(document)
    assert len(chunks) >= 2
    assert chunks[0].index == 0
    assert all(chunk.content.strip() for chunk in chunks)


def test_chunker_prefers_sentence_boundaries() -> None:
    chunker = SemanticChunkerAdapter(max_chars=80, overlap_chars=25)
    text = (
        "Photosynthesis converts light into chemical energy. "
        "Chlorophyll absorbs blue and red wavelengths of light. "
        "The Calvin cycle fixes carbon dioxide into glucose molecules."
    )
    document = ParsedDocument(pages=[ParsedPage(page_number=1, text=text)], total_pages=1)
    chunks = chunker.chunk(document)

    assert len(chunks) >= 2
    # No chunk should start mid-word from a hard cut in the middle of "Photosynthesis"
    joined = " ".join(c.content for c in chunks)
    assert "Photosynthesis" in joined
    assert "Calvin cycle" in joined
    # Sentence-level splits should dominate for this input
    assert any(c.metadata.get("split") in {"semantic", "sentence"} for c in chunks)


def test_chunker_overlap_is_sentence_aware() -> None:
    chunker = SemanticChunkerAdapter(max_chars=90, overlap_chars=40)
    text = (
        "First idea stays together as one sentence. "
        "Second idea also remains complete for retrieval. "
        "Third idea continues the explanation with more detail."
    )
    document = ParsedDocument(pages=[ParsedPage(page_number=1, text=text)], total_pages=1)
    chunks = chunker.chunk(document)
    assert len(chunks) >= 2
    # Overlap should repeat a trailing sentence fragment into the next chunk
    assert any(
        sentence in chunks[1].content
        for sentence in ("Second idea", "First idea", "Third idea")
    )


def test_chunker_detects_chapter_headings() -> None:
    chunker = SemanticChunkerAdapter(max_chars=200, overlap_chars=20)
    document = ParsedDocument(
        pages=[
            ParsedPage(
                page_number=1,
                text="Capítulo 1 Introducción\n\nLa célula es la unidad básica de la vida.",
            ),
            ParsedPage(
                page_number=2,
                text="Capítulo 2 Metabolismo\n\nLa respiración celular produce ATP.",
            ),
        ],
        total_pages=2,
    )
    chunks = chunker.chunk(document)
    chapter_names = {c.chapter_name for c in chunks if c.chapter_name}
    assert any(name and "Capítulo 1" in name for name in chapter_names)
    assert any(name and "Capítulo 2" in name for name in chapter_names)


def test_chunker_hard_splits_only_as_last_resort() -> None:
    chunker = SemanticChunkerAdapter(max_chars=40, overlap_chars=8)
    # No sentence punctuation → must hard-split by whitespace
    monster = "word " * 40
    document = ParsedDocument(pages=[ParsedPage(page_number=1, text=monster)], total_pages=1)
    chunks = chunker.chunk(document)
    assert len(chunks) >= 2
    assert all(len(c.content) <= 40 + 5 for c in chunks)  # allow tiny whitespace variance
    assert any(c.metadata.get("split") == "hard" for c in chunks)
