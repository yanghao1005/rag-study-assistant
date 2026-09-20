from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.domain.ports import TextChunker
from src.core.logging import logger

class LangChainTextChunker(TextChunker):
    def chunk(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)

    def chunk_with_metadata(
        self, 
        pages_data: List[Dict[str, Any]], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> List[Dict[str, Any]]:
        
        all_chunks = []
        for page in pages_data:
            text = page["text"]
            page_num = page["page_num"]
            chunks = self.chunk(text, chunk_size, chunk_overlap)
            
            for i, chunk_text in enumerate(chunks):
                all_chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "page_num": page_num,
                        "chunk_index": i,
                        "char_count": len(chunk_text)
                    }
                })
        return all_chunks
