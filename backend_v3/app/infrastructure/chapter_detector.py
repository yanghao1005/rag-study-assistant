import re
from typing import Any, Dict, List


CHAPTER_PATTERNS = [
    re.compile(r"Chapter\s+(\d+|[IVXLC]+)[:\s]+", re.IGNORECASE),
    re.compile(r"Section\s+\d+\.\d+", re.IGNORECASE),
]


def detect_chapters(pages: List[str]) -> List[Dict[str, Any]]:
    chapters: List[Dict[str, Any]] = []
    for page_index, page_text in enumerate(pages, start=1):
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        for line in lines[:3]:
            if any(pattern.search(line) for pattern in CHAPTER_PATTERNS):
                chapters.append(
                    {
                        "id": f"chapter-{len(chapters) + 1}",
                        "name": line,
                        "start_page": page_index,
                        "end_page": page_index,
                    }
                )
                break
    return chapters
