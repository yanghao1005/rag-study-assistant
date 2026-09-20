from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class PDFParser:
    def parse(self, file_path: str) -> list[dict]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            pages = []
            for index, page in enumerate(reader.pages):
                pages.append({"page": index + 1, "text": (page.extract_text() or "").strip()})
            return pages

        text = path.read_text(encoding="utf-8", errors="ignore")
        return [{"page": 1, "text": text.strip()}]
