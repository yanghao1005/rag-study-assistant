"""
Google Gemini embedding provider
Uses Google's text-embedding-004 model (768 dimensions)
"""
from typing import List
import google.generativeai as genai

from app.services.ai.base import BaseEmbedding
from app.core.logging import logger


class GeminiEmbeddingService(BaseEmbedding):
    """
    Google Gemini embedding provider
    Supports text-embedding-004 (768 dimensions)
    """
    
    # Model dimensions
    MODEL_DIMENSIONS = {
        "models/text-embedding-004": 768,
        "models/embedding-001": 768,
    }
    
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        """
        Initialize Gemini embeddings
        
        Args:
            api_key: Google AI API key
            model_name: Model name (text-embedding-004 recommended)
        """
        self.api_key = api_key
        self.model_name = model_name
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Set dimension
        self._dimension = self.MODEL_DIMENSIONS.get(model_name, 768)
        
        logger.info(f"Initialized Gemini embeddings: {model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Text string
            
        Returns:
            Embedding vector
        """
        if not text:
            return []
        
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings synchronously
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        logger.debug(f"Embedding {len(texts)} texts with Gemini")
        
        try:
            # Gemini supports batch embedding
            result = genai.embed_content(
                model=self.model_name,
                content=texts,
                task_type="retrieval_document",  # For document indexing
            )
            
            # Extract embeddings
            if hasattr(result, 'embedding'):
                # Single text
                return [result['embedding']]
            else:
                # Multiple texts
                return [emb for emb in result['embedding']]
        
        except Exception as e:
            logger.error(f"Error generating Gemini embeddings: {e}")
            raise
    
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings asynchronously
        Note: google-generativeai doesn't have native async, so we wrap sync
        """
        return self.embed_texts(texts)
    
    def get_dimension(self) -> int:
        """Return embedding dimension"""
        return self._dimension
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        Uses task_type="retrieval_query" for better retrieval
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        if not query:
            return []
        
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query",  # Optimized for queries
            )
            
            return result['embedding']
        
        except Exception as e:
            logger.error(f"Error generating Gemini query embedding: {e}")
            raise


# Testing
if __name__ == "__main__":
    import os
    import sys
    
    print("Testing Gemini Embeddings")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-key":
        print("❌ GEMINI_API_KEY not set in environment")
        print("   Get your key at: https://makersuite.google.com/app/apikey")
        print("   Set it with: $env:GEMINI_API_KEY='your-key'")
        sys.exit(1)
    
    service = GeminiEmbeddingService(api_key, "models/text-embedding-004")
    
    print(f"\n1. Model: text-embedding-004")
    print(f"   Dimension: {service.get_dimension()}")
    
    # Test documents
    texts = [
        "Machine learning is a subset of AI",
        "Neural networks process information",
    ]
    
    print(f"\n2. Embedding {len(texts)} documents...")
    doc_embeddings = service.embed_texts(texts)
    print(f"   ✅ Generated {len(doc_embeddings)} embeddings")
    print(f"   First 5 values: {doc_embeddings[0][:5]}")
    
    # Test query
    query = "What is artificial intelligence?"
    print(f"\n3. Embedding query: '{query}'")
    query_emb = service.embed_query(query)
    print(f"   ✅ Query embedding dimension: {len(query_emb)}")
    
    # Calculate similarity
    def cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b)
    
    print(f"\n4. Similarities:")
    print(f"   Query vs Doc1: {cosine_sim(query_emb, doc_embeddings[0]):.3f}")
    print(f"   Query vs Doc2: {cosine_sim(query_emb, doc_embeddings[1]):.3f}")
    
    print("\n✅ Test complete!")
