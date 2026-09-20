"""
Cohere embedding provider
Optimized for retrieval and RAG applications
"""
from typing import List
import httpx

from app.services.ai.base import BaseEmbedding
from app.core.logging import logger


class CohereEmbeddingService(BaseEmbedding):
    """
    Cohere embedding provider
    Supports embed-english-v3.0 and embed-multilingual-v3.0
    """
    
    # Model dimensions
    MODEL_DIMENSIONS = {
        "embed-english-v3.0": 1024,
        "embed-english-light-v3.0": 384,
        "embed-multilingual-v3.0": 1024,
        "embed-multilingual-light-v3.0": 384,
    }
    
    def __init__(self, api_key: str, model_name: str = "embed-english-v3.0"):
        """
        Initialize Cohere embeddings
        
        Args:
            api_key: Cohere API key
            model_name: Model name (embed-english-v3.0, etc.)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.cohere.ai/v1"
        
        # Set dimension
        self._dimension = self.MODEL_DIMENSIONS.get(model_name, 1024)
        
        logger.info(f"Initialized Cohere embeddings: {model_name}")
    
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
        
        logger.debug(f"Embedding {len(texts)} texts with Cohere")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "texts": texts,
            "model": self.model_name,
            "input_type": "search_document",  # For indexing documents
            "truncate": "END",  # Truncate long texts from end
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/embed",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                embeddings = data.get("embeddings", [])
                
                return embeddings
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Cohere API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error generating Cohere embeddings: {e}")
            raise
    
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings asynchronously
        """
        if not texts:
            return []
        
        logger.debug(f"Embedding {len(texts)} texts with Cohere (async)")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "texts": texts,
            "model": self.model_name,
            "input_type": "search_document",
            "truncate": "END",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embed",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                embeddings = data.get("embeddings", [])
                
                return embeddings
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Cohere API error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error generating Cohere embeddings: {e}")
            raise
    
    def get_dimension(self) -> int:
        """Return embedding dimension"""
        return self._dimension
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        Uses input_type="search_query" for better retrieval
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        if not query:
            return []
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "texts": [query],
            "model": self.model_name,
            "input_type": "search_query",  # Optimized for queries
            "truncate": "END",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embed",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                
                data = response.json()
                embeddings = data.get("embeddings", [])
                
                return embeddings[0] if embeddings else []
        
        except Exception as e:
            logger.error(f"Error generating Cohere query embedding: {e}")
            raise


# Testing
if __name__ == "__main__":
    import asyncio
    import sys
    import os
    
    print("Testing Cohere Embeddings")
    print("=" * 60)
    
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or api_key == "your-cohere-key":
        print("❌ COHERE_API_KEY not set in environment")
        print("   Set it with: export COHERE_API_KEY=your-key")
        sys.exit(1)
    
    async def test():
        service = CohereEmbeddingService(api_key, "embed-english-v3.0")
        
        print(f"\n1. Model: embed-english-v3.0")
        print(f"   Dimension: {service.get_dimension()}")
        
        # Test documents
        texts = [
            "Machine learning is a subset of AI",
            "Neural networks process information",
        ]
        
        print(f"\n2. Embedding {len(texts)} documents...")
        doc_embeddings = await service.aembed_texts(texts)
        print(f"   ✅ Generated {len(doc_embeddings)} embeddings")
        print(f"   First 5 values: {doc_embeddings[0][:5]}")
        
        # Test query
        query = "What is artificial intelligence?"
        print(f"\n3. Embedding query: '{query}'")
        query_emb = await service.embed_query(query)
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
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test())
