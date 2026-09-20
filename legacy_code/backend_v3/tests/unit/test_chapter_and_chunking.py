from app.infrastructure.chapter_detector import detect_chapters
from app.infrastructure.chunker import split_chunks


def test_detect_chapters_matches_required_patterns() -> None:
    pages = [
        "Chapter 1: Introduction\nSome content",
        "Section 1.1 Basics\nMore content",
        "No chapter here",
    ]
    chapters = detect_chapters(pages)
    assert len(chapters) == 2
    assert chapters[0]["name"].startswith("Chapter 1")
    assert chapters[1]["name"].startswith("Section 1.1")


def test_split_chunks_adds_required_metadata() -> None:
    pages = ["Chapter 1: Intro\nThis is a test document page."]
    chapters = [{"id": "chapter-1", "name": "Chapter 1: Intro", "start_page": 1, "end_page": 1}]

    chunks = split_chunks(
        pages=pages,
        chunk_size=1000,
        chunk_overlap=200,
        subject_id="subject-1",
        document_type="pdf",
        chapters=chapters,
    )

    assert len(chunks) >= 1
    metadata = chunks[0]["metadata"]
    assert metadata["subject_id"] == "subject-1"
    assert metadata["document_type"] == "pdf"
    assert metadata["page"] == 1
    assert metadata["chapter_name"] == "Chapter 1: Intro"
