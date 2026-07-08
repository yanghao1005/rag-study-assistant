"""
OpenAI implementation
"""
from typing import List
from openai import OpenAI, AsyncOpenAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.services.ai.base import BaseLLM, BaseEmbedding
from app.core.config import settings
from app.core.logging import logger


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation"""
    
    def __init__(self):
        config = settings.get_llm_config()
        self.model = config["model"]
        self.client = OpenAI(api_key=config["api_key"])
        self.async_client = AsyncOpenAI(api_key=config["api_key"])
        
        # LangChain wrapper
        self.langchain_llm = ChatOpenAI(
            model=self.model,
            api_key=config["api_key"],
            temperature=config.get("temperature", 0.7)
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Async generate text using OpenAI"""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI async generation error: {e}")
            raise


class OpenAIEmbeddingService(BaseEmbedding):
    """OpenAI embedding implementation"""
    
    def __init__(self):
        config = settings.get_embedding_config()
        self.model = config["model"]
        self.client = OpenAI(api_key=config["api_key"])
        self.async_client = AsyncOpenAI(api_key=config["api_key"])
        
        # LangChain wrapper
        self.langchain_embeddings = OpenAIEmbeddings(
            model=self.model,
            api_key=config["api_key"]
        )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """Async generate embeddings"""
        try:
            response = await self.async_client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI async embedding error: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return dimensions.get(self.model, 1536)
