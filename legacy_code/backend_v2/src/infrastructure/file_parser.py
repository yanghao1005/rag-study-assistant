import fitz  # PyMuPDF
from typing import Dict, List, Any
from pathlib import Path
from src.domain.ports import FileParser
from src.core.logging import logger

class PyMuPDFParser(FileParser):
    def parse(self, file_path: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            doc = fitz.open(file_path)
            metadata = {
                "total_pages": len(doc),
                "author": doc.metadata.get("author", ""),
                "title": doc.metadata.get("title", ""),
                "subject": doc.metadata.get("subject", ""),
            }
            
            pages_data = []
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                pages_data.append({
                    "page_num": page_num + 1,
                    "text": text,
                    "char_count": len(text)
                })
            
            doc.close()
            return metadata, pages_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise
