"""
Factory for creating AI service instances
Easy switching between providers via environment variables
"""
from app.core.config import settings, AIProvider, EmbeddingProvider
from app.services.ai.base import BaseLLM, BaseEmbedding
from app.core.logging import logger


def get_llm() -> BaseLLM:
    """
    Factory function to get LLM instance based on configuration
    
    To switch providers, just change AI_PROVIDER in .env:
    - AI_PROVIDER=openai
    - AI_PROVIDER=ollama
    - AI_PROVIDER=huggingface
    - AI_PROVIDER=cohere
    - AI_PROVIDER=anthropic
    """
    provider = settings.ai_provider
    logger.info(f"Initializing LLM provider: {provider}")
    
    if provider == AIProvider.OPENAI:
        from app.services.ai.openai_provider import OpenAILLM
        return OpenAILLM()
    
    elif provider == AIProvider.OLLAMA:
        from app.services.ai.ollama_provider import OllamaLLM
        return OllamaLLM()
    
    elif provider == AIProvider.HUGGINGFACE:
        # from app.services.ai.huggingface_provider import HuggingFaceLLM
        # return HuggingFaceLLM()
        raise NotImplementedError("HuggingFace provider not yet implemented")
    
    elif provider == AIProvider.COHERE:
        # from app.services.ai.cohere_provider import CohereLLM
        # return CohereLLM()
        raise NotImplementedError("Cohere provider not yet implemented")
    
    elif provider == AIProvider.ANTHROPIC:
        # from app.services.ai.anthropic_provider import AnthropicLLM
        # return AnthropicLLM()
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    else:
        raise ValueError(f"Unknown AI provider: {provider}")


def get_embedding_service() -> BaseEmbedding:
    """
    Factory function to get embedding service based on configuration
    
    To switch providers, just change EMBEDDING_PROVIDER in .env:
    - EMBEDDING_PROVIDER=openai
    - EMBEDDING_PROVIDER=ollama
    - EMBEDDING_PROVIDER=huggingface
    - EMBEDDING_PROVIDER=cohere
    """
    provider = settings.embedding_provider
    logger.info(f"Initializing embedding provider: {provider}")
    
    if provider == EmbeddingProvider.OPENAI:
        from app.services.ai.openai_provider import OpenAIEmbeddingService
        return OpenAIEmbeddingService()
    
    elif provider == EmbeddingProvider.OLLAMA:
        from app.services.ai.ollama_provider import OllamaEmbeddingService
        return OllamaEmbeddingService()
    
    elif provider == EmbeddingProvider.HUGGINGFACE:
        from app.services.ai.huggingface_provider import HuggingFaceEmbeddingService
        return HuggingFaceEmbeddingService(
            model_name=settings.huggingface_embedding_model,
            api_key=settings.huggingface_api_key
        )
    
    elif provider == EmbeddingProvider.COHERE:
        from app.services.ai.cohere_provider import CohereEmbeddingService
        return CohereEmbeddingService(
            api_key=settings.cohere_api_key,
            model_name=settings.cohere_embedding_model
        )
    
    elif provider == EmbeddingProvider.GEMINI:
        from app.services.ai.gemini_provider import GeminiEmbeddingService
        return GeminiEmbeddingService(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_embedding_model
        )
    
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")


# Global instances (lazy initialized)
_llm_instance: BaseLLM = None
_embedding_instance: BaseEmbedding = None


def get_llm_instance() -> BaseLLM:
    """Get or create LLM singleton"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_llm()
    return _llm_instance


def get_embedding_instance() -> BaseEmbedding:
    """Get or create embedding singleton"""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = get_embedding_service()
    return _embedding_instance
