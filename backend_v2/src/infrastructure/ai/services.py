from typing import List
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
