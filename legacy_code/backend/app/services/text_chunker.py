"""
Text chunking service with metadata enrichment
Uses LangChain RecursiveCharacterTextSplitter for semantic-aware chunking
"""
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logging import logger


# Default chunking parameters
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def chunk_text_with_metadata(
    text: str,
    page_num: int,
    chapter: Optional[Dict] = None,
    subject_id: Optional[str] = None,
    document_id: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Split text into chunks with metadata enrichment
    
    Args:
        text: Text content to chunk
        page_num: Page number this text came from
        chapter: Chapter dict with name, start_page, end_page (optional)
        subject_id: Subject UUID from database
        document_id: Document UUID from database
        chunk_size: Max characters per chunk
        chunk_overlap: Overlapping characters between chunks
        
    Returns:
        List of chunk dicts with metadata:
        [{
            "content": "chunk text...",
            "metadata": {
                "page_num": 5,
                "chapter_name": "Chapter 2",
                "subject_id": "uuid",
                "document_id": "uuid",
                "chunk_index": 0,
                "char_count": 987
            }
        }]
    """
    if not text or not text.strip():
        logger.warning(f"Empty text provided for chunking on page {page_num}")
        return []
    
    # Initialize text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",  # Paragraph breaks (highest priority)
            "\n",    # Line breaks
            ". ",    # Sentence ends
            ", ",    # Clause breaks
            " ",     # Word breaks
            "",      # Character breaks (last resort)
        ]
    )
    
    # Split the text
    chunks = splitter.split_text(text)
    
    logger.debug(
        f"Split page {page_num} ({len(text)} chars) into {len(chunks)} chunks"
    )
    
    # Enrich each chunk with metadata
    enriched_chunks = []
    for idx, chunk in enumerate(chunks):
        metadata = {
            "page_num": page_num,
            "chunk_index": idx,
            "char_count": len(chunk),
        }
        
        # Add chapter info if available
        if chapter:
            metadata["chapter_name"] = chapter.get("name")
            metadata["chapter_order"] = chapter.get("order_index")
        
        # Add IDs if provided
        if subject_id:
            metadata["subject_id"] = subject_id
        if document_id:
            metadata["document_id"] = document_id
        
        enriched_chunks.append({
            "content": chunk,
            "metadata": metadata,
        })
    
    return enriched_chunks


def chunk_pages_text(
    pages_text: List[Dict],
    chapters: List[Dict],
    subject_id: Optional[str] = None,
    document_id: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Chunk all pages from a document with chapter detection
    
    Args:
        pages_text: List of page data from pdf_parser
                   [{"page_num": 1, "text": "...", "char_count": 1500}]
        chapters: List of detected chapters with boundaries
        subject_id: Subject UUID
        document_id: Document UUID
        chunk_size: Max characters per chunk
        chunk_overlap: Overlapping characters between chunks
        
    Returns:
        List of all chunks from all pages with enriched metadata
    """
    all_chunks = []
    
    for page in pages_text:
        page_num = page["page_num"]
        text = page["text"]
        
        # Find which chapter this page belongs to
        chapter = None
        for ch in chapters:
            if ch["start_page"] <= page_num <= ch["end_page"]:
                chapter = ch
                break
        
        # Chunk the page text
        chunks = chunk_text_with_metadata(
            text=text,
            page_num=page_num,
            chapter=chapter,
            subject_id=subject_id,
            document_id=document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        all_chunks.extend(chunks)
    
    logger.info(
        f"Created {len(all_chunks)} total chunks from {len(pages_text)} pages"
    )
    
    return all_chunks


def chunk_summary(
    summary_text: str,
    subject_id: Optional[str] = None,
    document_id: Optional[str] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict]:
    """
    Chunk summary text (no page/chapter metadata)
    
    Args:
        summary_text: Summary text to chunk
        subject_id: Subject UUID
        document_id: Document UUID
        chunk_size: Max characters per chunk
        chunk_overlap: Overlapping characters between chunks
        
    Returns:
        List of chunks with summary-specific metadata
    """
    if not summary_text or not summary_text.strip():
        logger.warning("Empty summary text provided")
        return []
    
    # Use text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
        separators=["\n\n", "\n", ". ", ", ", " ", ""]
    )
    
    chunks = splitter.split_text(summary_text)
    
    logger.info(f"Created {len(chunks)} chunks from summary text")
    
    # Enrich with metadata
    enriched_chunks = []
    for idx, chunk in enumerate(chunks):
        metadata = {
            "chunk_index": idx,
            "char_count": len(chunk),
            "is_summary": True,  # Flag to distinguish from PDF chunks
        }
        
        if subject_id:
            metadata["subject_id"] = subject_id
        if document_id:
            metadata["document_id"] = document_id
        
        enriched_chunks.append({
            "content": chunk,
            "metadata": metadata,
        })
    
    return enriched_chunks


def merge_small_chunks(
    chunks: List[Dict],
    min_chunk_size: int = 100,
    max_chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> List[Dict]:
    """
    Merge very small chunks with adjacent chunks to improve quality
    
    Args:
        chunks: List of chunks from chunk_text_with_metadata
        min_chunk_size: Minimum desirable chunk size (chars)
        max_chunk_size: Maximum chunk size to avoid going over
        
    Returns:
        List of chunks with small ones merged
    """
    if not chunks:
        return []
    
    merged = []
    buffer = None
    
    for chunk in chunks:
        content = chunk["content"]
        char_count = len(content)
        
        # If this chunk is large enough, add it
        if char_count >= min_chunk_size:
            # If we have a buffer, add it first
            if buffer:
                merged.append(buffer)
                buffer = None
            merged.append(chunk)
        else:
            # Chunk is too small, try to merge
            if buffer is None:
                buffer = chunk
            else:
                # Merge with buffer if under max size
                combined_size = len(buffer["content"]) + len(content)
                if combined_size <= max_chunk_size:
                    buffer["content"] += " " + content
                    buffer["metadata"]["char_count"] = len(buffer["content"])
                else:
                    # Can't merge, add buffer and start new one
                    merged.append(buffer)
                    buffer = chunk
    
    # Add final buffer if exists
    if buffer:
        merged.append(buffer)
    
    if len(merged) < len(chunks):
        logger.info(f"Merged {len(chunks)} chunks into {len(merged)} chunks")
    
    return merged


def get_chunk_stats(chunks: List[Dict]) -> Dict:
    """
    Calculate statistics about chunk distribution
    
    Args:
        chunks: List of chunks
        
    Returns:
        Dict with stats: total, avg_size, min_size, max_size, pages_covered
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_size": 0,
            "min_size": 0,
            "max_size": 0,
            "pages_covered": 0,
        }
    
    sizes = [c["metadata"]["char_count"] for c in chunks]
    pages = set()
    
    for chunk in chunks:
        if "page_num" in chunk["metadata"]:
            pages.add(chunk["metadata"]["page_num"])
    
    return {
        "total_chunks": len(chunks),
        "avg_size": sum(sizes) // len(sizes),
        "min_size": min(sizes),
        "max_size": max(sizes),
        "pages_covered": len(pages),
    }


# Testing
if __name__ == "__main__":
    # Example usage
    sample_text = """
    This is a sample paragraph that demonstrates text chunking functionality.
    The text splitter will attempt to break this text at natural boundaries.
    
    This is a second paragraph. It contains multiple sentences. Each sentence
    provides some information. The chunker should respect paragraph breaks.
    
    And here is a third paragraph with additional content that extends
    the total length of the text to ensure multiple chunks are created.
    """ * 5  # Repeat to make it longer
    
    chunks = chunk_text_with_metadata(
        text=sample_text,
        page_num=1,
        chapter={"name": "Chapter 1", "order_index": 0},
        chunk_size=200,
        chunk_overlap=50,
    )
    
    print(f"\n=== Created {len(chunks)} chunks ===")
    for idx, chunk in enumerate(chunks):
        print(f"\nChunk {idx + 1}:")
        print(f"  Size: {chunk['metadata']['char_count']} chars")
        print(f"  Page: {chunk['metadata']['page_num']}")
        print(f"  Chapter: {chunk['metadata'].get('chapter_name', 'None')}")
        print(f"  Preview: {chunk['content'][:80]}...")
    
    stats = get_chunk_stats(chunks)
    print(f"\n=== Stats ===")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Avg size: {stats['avg_size']} chars")
    print(f"Range: {stats['min_size']}-{stats['max_size']} chars")
