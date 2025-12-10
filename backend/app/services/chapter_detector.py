"""
Chapter detection service for PDF documents
Uses regex patterns to automatically detect chapter boundaries
"""
import re
from typing import List, Dict, Optional

from app.core.logging import logger


# Common chapter heading patterns
CHAPTER_PATTERNS = [
    # "Chapter 1: Introduction", "Chapter I: Overview"
    r'^Chapter\s+(\d+|[IVXLC]+)[:\s]+(.+)$',
    
    # "Section 1.1: Background", "Section 2.3.4"
    r'^Section\s+(\d+(?:\.\d+)*)[:\s]+(.+)$',
    
    # "1. Introduction", "2. Methodology"
    r'^(\d+)\.\s+([A-Z][^.]+)$',
    
    # "I. Overview", "II. Methods"
    r'^([IVXLC]+)\.\s+([A-Z][^.]+)$',
    
    # "1 INTRODUCTION" (all caps)
    r'^(\d+)\s+([A-Z][A-Z\s]{3,})$',
    
    # "CHAPTER 1" or "CHAPTER ONE"
    r'^CHAPTER\s+(\d+|[IVXLC]+|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)',
]


def detect_chapters(pages_text: List[Dict]) -> List[Dict]:
    """
    Detect chapter boundaries from extracted PDF text
    
    Args:
        pages_text: List of page data from pdf_parser
                   [{"page_num": 1, "text": "...", "char_count": 1500}]
    
    Returns:
        List of detected chapters:
        [{"name": "Chapter 1: Introduction", 
          "start_page": 1, 
          "start_line": 5,
          "detected_by": "pattern_index"}]
    """
    chapters = []
    
    for page in pages_text:
        page_num = page["page_num"]
        lines = page["text"].split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines or very short lines
            if len(line) < 3:
                continue
            
            # Try each pattern
            for pattern_idx, pattern in enumerate(CHAPTER_PATTERNS):
                match = re.match(pattern, line, re.IGNORECASE | re.MULTILINE)
                
                if match:
                    chapter = {
                        "name": line,
                        "start_page": page_num,
                        "start_line": line_num,
                        "detected_by": f"pattern_{pattern_idx}",
                        "pattern": pattern,
                    }
                    chapters.append(chapter)
                    logger.debug(
                        f"Detected chapter at page {page_num}, line {line_num}: {line}"
                    )
                    break  # Stop after first match for this line
    
    logger.info(f"Detected {len(chapters)} potential chapters")
    return chapters


def merge_chapter_boundaries(chapters: List[Dict], total_pages: int) -> List[Dict]:
    """
    Merge detected chapters and set end_page for each
    
    Args:
        chapters: List of detected chapters from detect_chapters()
        total_pages: Total number of pages in document
        
    Returns:
        List of chapters with end_page set:
        [{"name": "...", "start_page": 1, "end_page": 15, "order_index": 0}]
    """
    if not chapters:
        logger.warning("No chapters detected")
        return []
    
    # Sort by start_page, then by start_line
    sorted_chapters = sorted(
        chapters,
        key=lambda c: (c["start_page"], c.get("start_line", 0))
    )
    
    # Remove duplicates (same page, similar names)
    deduplicated = []
    for chapter in sorted_chapters:
        # Check if this is too similar to the last added chapter
        if deduplicated:
            last = deduplicated[-1]
            # If on same page and name is similar, skip
            if (chapter["start_page"] == last["start_page"] and 
                chapter["name"].lower() == last["name"].lower()):
                continue
        deduplicated.append(chapter)
    
    # Set end_page for each chapter
    result = []
    for idx, chapter in enumerate(deduplicated):
        # End page is one before next chapter starts, or last page
        if idx < len(deduplicated) - 1:
            end_page = deduplicated[idx + 1]["start_page"] - 1
        else:
            end_page = total_pages
        
        # Ensure end_page is at least start_page
        if end_page < chapter["start_page"]:
            end_page = chapter["start_page"]
        
        result.append({
            "name": chapter["name"],
            "start_page": chapter["start_page"],
            "end_page": end_page,
            "order_index": idx,
            "detected_by": chapter.get("detected_by", "unknown"),
        })
    
    logger.info(
        f"Merged into {len(result)} chapters spanning "
        f"pages {result[0]['start_page']}-{result[-1]['end_page']}"
    )
    
    return result


def find_chapter_for_page(page_num: int, chapters: List[Dict]) -> Optional[Dict]:
    """
    Find which chapter a specific page belongs to
    
    Args:
        page_num: Page number (1-indexed)
        chapters: List of chapters with start_page and end_page
        
    Returns:
        Chapter dict if found, None otherwise
    """
    for chapter in chapters:
        if chapter["start_page"] <= page_num <= chapter["end_page"]:
            return chapter
    
    return None


def validate_chapters(chapters: List[Dict], total_pages: int) -> List[str]:
    """
    Validate chapter structure and return warnings
    
    Args:
        chapters: List of chapters
        total_pages: Total pages in document
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    if not chapters:
        warnings.append("No chapters detected in document")
        return warnings
    
    # Check for gaps in page coverage
    covered_pages = set()
    for chapter in chapters:
        for page in range(chapter["start_page"], chapter["end_page"] + 1):
            covered_pages.add(page)
    
    all_pages = set(range(1, total_pages + 1))
    uncovered = all_pages - covered_pages
    
    if uncovered:
        warnings.append(
            f"{len(uncovered)} pages not covered by any chapter: "
            f"{sorted(list(uncovered))[:10]}"
        )
    
    # Check for very short chapters (< 2 pages)
    short_chapters = [
        c for c in chapters 
        if c["end_page"] - c["start_page"] < 1
    ]
    if short_chapters:
        warnings.append(
            f"{len(short_chapters)} chapters are very short (1 page or less)"
        )
    
    # Check for overlaps
    for i, chapter1 in enumerate(chapters):
        for chapter2 in chapters[i+1:]:
            if not (chapter1["end_page"] < chapter2["start_page"] or
                    chapter2["end_page"] < chapter1["start_page"]):
                warnings.append(
                    f"Chapters overlap: '{chapter1['name']}' and '{chapter2['name']}'"
                )
    
    return warnings


def detect_and_merge_chapters(pages_text: List[Dict]) -> List[Dict]:
    """
    Convenience function: detect chapters and merge boundaries in one call
    
    Args:
        pages_text: List of page data from pdf_parser
        
    Returns:
        List of finalized chapters with start_page and end_page
    """
    if not pages_text:
        logger.warning("No pages provided for chapter detection")
        return []
    
    # Detect chapters
    detected = detect_chapters(pages_text)
    
    if not detected:
        logger.info("No chapters detected, document will be treated as single unit")
        return []
    
    # Merge and set boundaries
    total_pages = max(p["page_num"] for p in pages_text)
    merged = merge_chapter_boundaries(detected, total_pages)
    
    # Validate and log warnings
    warnings = validate_chapters(merged, total_pages)
    for warning in warnings:
        logger.warning(f"Chapter validation: {warning}")
    
    return merged


# Testing
if __name__ == "__main__":
    # Example usage
    sample_pages = [
        {
            "page_num": 1,
            "text": "Title Page\nBy Author\nPublisher 2024",
            "char_count": 35
        },
        {
            "page_num": 2,
            "text": "Chapter 1: Introduction\n\nThis is the introduction to the document...",
            "char_count": 100
        },
        {
            "page_num": 5,
            "text": "Chapter 2: Methodology\n\nThis chapter describes the methods...",
            "char_count": 100
        },
        {
            "page_num": 10,
            "text": "Section 3.1: Results\n\nThe results show that...",
            "char_count": 80
        },
    ]
    
    chapters = detect_and_merge_chapters(sample_pages)
    
    print("\n=== Detected Chapters ===")
    for chapter in chapters:
        print(f"{chapter['order_index'] + 1}. {chapter['name']}")
        print(f"   Pages: {chapter['start_page']}-{chapter['end_page']}")
        print(f"   Detected by: {chapter['detected_by']}")
        print()
