"""
Ollama implementation (for local models)
"""
from typing import List
import httpx

from app.services.ai.base import BaseLLM, BaseEmbedding
from app.core.config import settings
from app.core.logging import logger


class OllamaLLM(BaseLLM):
    """Ollama LLM implementation"""
    
    def __init__(self):
        config = settings.get_llm_config()
        self.base_url = config["base_url"]
        self.model = config["model"]
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama"""
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        **kwargs
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Async generate text using Ollama"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        **kwargs
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama async generation error: {e}")
            raise


class OllamaEmbeddingService(BaseEmbedding):
    """Ollama embedding implementation"""
    
    def __init__(self):
        config = settings.get_embedding_config()
        self.base_url = config["base_url"]
        self.model = config["model"]
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = []
            with httpx.Client() as client:
                for text in texts:
                    response = client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": self.model, "prompt": text},
                        timeout=30.0
                    )
                    response.raise_for_status()
                    embeddings.append(response.json()["embedding"])
            return embeddings
        except Exception as e:
            logger.error(f"Ollama embedding error: {e}")
            raise
    
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """Async generate embeddings"""
        try:
            embeddings = []
            async with httpx.AsyncClient() as client:
                for text in texts:
                    response = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={"model": self.model, "prompt": text},
                        timeout=30.0
                    )
                    response.raise_for_status()
                    embeddings.append(response.json()["embedding"])
            return embeddings
        except Exception as e:
            logger.error(f"Ollama async embedding error: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension (Ollama models vary)"""
        # Most Ollama embedding models use these dimensions
        dimensions = {
            "nomic-embed-text": 768,
            "mxbai-embed-large": 1024,
            "all-minilm": 384,
        }
        return dimensions.get(self.model, 768)
