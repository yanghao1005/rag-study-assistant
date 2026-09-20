from pathlib import Path
from typing import Any, Dict, List


def parse_pdf_file(file_path: str) -> Dict[str, Any]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF parsing") from exc

    path = Path(file_path)
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise ValueError("Invalid PDF file path")

    pages: List[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            pages.append(page.get_text("text").strip())

    return {
        "pages": pages,
        "total_pages": len(pages),
        "metadata": {
            "source_file": str(path),
        },
    }


def parse_summary_text(document_text: str) -> Dict[str, Any]:
    normalized = document_text.strip()
    return {
        "pages": [normalized] if normalized else [],
        "total_pages": 1 if normalized else 0,
        "metadata": {},
    }
