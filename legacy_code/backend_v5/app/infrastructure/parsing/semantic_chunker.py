from __future__ import annotations

from typing import Any


class SemanticChunker:
    def chunk(self, *, pages: list[dict[str, Any]], chunk_size: int = 900, overlap: int = 120) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        for page in pages:
            text = str(page.get("text") or "").strip()
            page_num = int(page.get("page") or 1)
            if not text:
                continue

            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                content = text[start:end].strip()
                if content:
                    chunks.append(
                        {
                            "content": content,
                            "page": page_num,
                            "chapter_name": None,
                            "document_type": "pdf",
                            "metadata": {"char_start": start, "char_end": end},
                        }
                    )
                if end >= len(text):
                    break
                start = max(0, end - overlap)

        return chunks
