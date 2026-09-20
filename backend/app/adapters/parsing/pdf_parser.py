"""PyPDF document parser adapter."""

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from app.ports.parsing import DocumentParserPort, ParsedDocument, ParsedPage


class PyPdfParserAdapter(DocumentParserPort):
    async def parse(self, data: bytes, *, filename: str) -> ParsedDocument:
        reader = PdfReader(BytesIO(data))
        pages: list[ParsedPage] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            pages.append(ParsedPage(page_number=index, text=text))

        metadata = {"filename": filename, "parser": "pypdf"}
        if reader.metadata:
            title = reader.metadata.title
            if title:
                metadata["title"] = str(title)

        return ParsedDocument(pages=pages, total_pages=len(pages), metadata=metadata)
