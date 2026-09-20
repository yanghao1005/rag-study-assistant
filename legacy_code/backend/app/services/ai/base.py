"""
Abstract base classes for AI services
"""
from abc import ABC, abstractmethod
from typing import List


class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def agenerate(self, prompt: str, **kwargs) -> str:
        """Async generate text from prompt"""
        pass


class BaseEmbedding(ABC):
    """Base class for embedding providers"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass
    
    @abstractmethod
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """Async generate embeddings for multiple texts"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass
