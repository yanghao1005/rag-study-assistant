from typing import Any, Dict, List, Optional


def _find_chapter(page_number: int, chapters: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for chapter in chapters:
        if chapter["start_page"] <= page_number <= chapter["end_page"]:
            return chapter
    return None


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
        )
        return [chunk for chunk in splitter.split_text(text) if chunk.strip()]
    except Exception:
        chunks: List[str] = []
        step = max(1, chunk_size - chunk_overlap)
        cursor = 0
        while cursor < len(text):
            chunks.append(text[cursor : cursor + chunk_size])
            cursor += step
        return [chunk.strip() for chunk in chunks if chunk.strip()]


def split_chunks(
    pages: List[str],
    chunk_size: int,
    chunk_overlap: int,
    subject_id: str | None,
    document_type: str,
    chapters: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for page_number, page_text in enumerate(pages, start=1):
        chapter = _find_chapter(page_number, chapters)
        chapter_name = chapter["name"] if chapter else None
        chapter_id = chapter.get("id") if chapter else None
        for chunk_text in _split_text(page_text, chunk_size, chunk_overlap):
            chunks.append(
                {
                    "content": chunk_text,
                    "metadata": {
                        "subject_id": subject_id,
                        "document_type": document_type,
                        "page": page_number if document_type == "pdf" else None,
                        "chapter_id": chapter_id,
                        "chapter_name": chapter_name,
                    },
                }
            )
    return chunks
