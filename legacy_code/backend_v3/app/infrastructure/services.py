import hashlib
from typing import Any, Dict, List

from app.infrastructure.chapter_detector import detect_chapters
from app.infrastructure.chunker import split_chunks
from app.infrastructure.pdf_parser import parse_pdf_file, parse_summary_text


def parse_document(document_type: str, document_text: str | None = None, file_path: str | None = None) -> Dict[str, Any]:
    if document_type == "pdf":
        if not file_path:
            return parse_summary_text(document_text or "")
        return parse_pdf_file(file_path)
    return parse_summary_text(document_text or "")


def chunk_document(
    pages: List[str],
    chunk_size: int,
    chunk_overlap: int,
    subject_id: str | None,
    document_type: str,
    chapters: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return split_chunks(
        pages=pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        subject_id=subject_id,
        document_type=document_type,
        chapters=chapters,
    )


def generate_embeddings(chunks: List[Dict[str, Any]], model: str, api_key: str | None = None) -> List[List[float]]:
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            texts = [chunk["content"] for chunk in chunks]
            response = client.embeddings.create(model=model, input=texts)
            return [item.embedding for item in response.data]
        except Exception:
            pass

    embeddings: List[List[float]] = []
    for chunk in chunks:
        digest = hashlib.sha256(chunk["content"].encode("utf-8")).digest()
        vector = [round(digest[index % len(digest)] / 255, 6) for index in range(1536)]
        embeddings.append(vector)
    return embeddings


def build_document_index(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    merged = " ".join(chunk["content"] for chunk in chunks[:12])
    return {"synopsis": merged[:1200], "chunk_count": len(chunks)}


def retrieve_context(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for row in rows:
        normalized.append(
            {
                "content": row.get("content", ""),
                "metadata": row.get("metadata", {}),
            }
        )
    return normalized


def generate_output(query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    sources = []
    for chunk in context_chunks:
        metadata = chunk.get("metadata", {})
        sources.append(
            {
                "document_type": metadata.get("document_type"),
                "page": metadata.get("page"),
                "chapter_name": metadata.get("chapter_name"),
                "preview": chunk.get("content", "")[:180],
            }
        )
    answer = " ".join(chunk.get("content", "")[:220] for chunk in context_chunks[:3]).strip()
    return {"query": query, "answer": answer, "sources": sources}
