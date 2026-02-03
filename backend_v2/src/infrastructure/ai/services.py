from typing import List, Dict, Any
import json
import re
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from src.domain.ports import LLMService, EmbeddingService
from src.config import get_settings
from src.core.logging import logger

class OpenAIEmbeddingService(EmbeddingService):
    def __init__(self):
        settings = get_settings()
        self.model = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model=settings.DEFAULT_EMBEDDING_MODEL or "text-embedding-3-small"
        )

    async def embed_text(self, text: str) -> List[float]:
        return await self.model.aembed_query(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return await self.model.aembed_documents(texts)

class OpenAILLMService(LLMService):
    def __init__(self):
        settings = get_settings()
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.DEFAULT_LLM_MODEL,
            temperature=0.7
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise

    async def generate_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a global summary and a structured index from chunks.
        """
        # 1. Prepare context (simplify to avoid token limits, take first N chars of each chunk or first few chunks)
        # For a more robust solution, we'd use map-reduce, but here we'll take a representative sample.
        # Let's take the first 80000 characters combined approx.
        
        context_parts = []
        current_len = 0
        MAX_LEN = 80000 
        
        for chunk in chunks:
            content = chunk.get("content", "")
            if current_len + len(content) > MAX_LEN:
                break
            context_parts.append(f"[Chunk {chunk.get('metadata', {}).get('chunk_index')}]: {content}")
            current_len += len(content)
            
        context = "\n\n".join(context_parts)
        
        prompt = f"""
        You are an expert document analyzer. 
        Your task is to create a structured index for the provided document content.
        
        1. Create a Global Summary (approx 3-5 sentences).
        2. Identify Key Topics.
        3. Create a one-line description for each Chunk ID provided in the context.
        
        Output MUST be valid JSON with the following structure:
        {{
            "document_summary": "...",
            "key_topics": ["topic1", "topic2"],
            "chunk_map": [
                {{
                    "chunk_index": 0,
                    "description": "...",
                    "page_num": 1
                }}
            ]
        }}
        
        IMPORTANT: 
        - Only include chunks present in the input.
        - Ensure JSON is valid.
        
        Content:
        {context}
        """
        
        try:
            # Enforce JSON mode if supported or just ask nicely (using generic generate for now)
            # For strict JSON, we should probably use response_format={"type": "json_object"} if using newer OpenAI client,
            # but wrapping .generate() is safer with existing setup.
            
            # Using self.llm which is ChatOpenAI. 
            # We can try to use .invoke with bind(response_format=...) if we cast, but let's stick to text + parsing.
            
            response_text = await self.generate(prompt)
            
            # Clean possible markdown code blocks
            json_str = response_text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to generate index: {e}")
            # Return empty structure on failure
            return {
                "document_summary": "Error generating summary.",
                "key_topics": [],
                "chunk_map": []
            }

class HuggingFaceEmbeddingService(EmbeddingService):
    def __init__(self):
        settings = get_settings()
        self.model_name = settings.DEFAULT_EMBEDDING_MODEL
        logger.info(f"Loading HuggingFace model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
    
    async def embed_text(self, text: str) -> List[float]:
        if not text:
            return []
        embeddings = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        return embeddings[0].tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()
