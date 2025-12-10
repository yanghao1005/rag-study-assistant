"""
HuggingFace embedding provider using sentence-transformers
Supports local and API-based models
"""
from typing import List
from sentence_transformers import SentenceTransformer

from app.services.ai.base import BaseEmbedding
from app.core.logging import logger


class HuggingFaceEmbeddingService(BaseEmbedding):
    """
    HuggingFace embedding provider
    Uses sentence-transformers library for local inference
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        Initialize HuggingFace embeddings
        
        Args:
            model_name: Model name from HuggingFace Hub
                       e.g., "sentence-transformers/all-MiniLM-L6-v2"
            api_key: Optional HF API key for private models
        """
        self.model_name = model_name
        self.api_key = api_key
        
        logger.info(f"Loading HuggingFace model: {model_name}")
        
        # Load model locally (downloads if not cached)
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded (dimension: {self._dimension})")
    
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
        
        logger.debug(f"Embedding {len(texts)} texts with HuggingFace")
        
        # Encode texts (returns numpy array)
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,  # L2 normalization for better cosine similarity
        )
        
        # Convert numpy to list of lists
        return [emb.tolist() for emb in embeddings]
    
    async def aembed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings asynchronously
        Note: sentence-transformers is synchronous, so we just wrap it
        """
        return self.embed_texts(texts)
    
    def get_dimension(self) -> int:
        """Return embedding dimension"""
        return self._dimension


# Common HuggingFace embedding models
HUGGINGFACE_MODELS = {
    # Fast models (384 dim)
    "all-MiniLM-L6-v2": {
        "full_name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384,
        "description": "Fast, good for development/testing",
    },
    
    # Balanced models (768 dim)
    "all-mpnet-base-v2": {
        "full_name": "sentence-transformers/all-mpnet-base-v2",
        "dimension": 768,
        "description": "Best quality among sentence-transformers",
    },
    
    # Specialized models (1024 dim)
    "bge-large-en-v1.5": {
        "full_name": "BAAI/bge-large-en-v1.5",
        "dimension": 1024,
        "description": "State-of-the-art for English, optimized for retrieval",
    },
    "bge-base-en-v1.5": {
        "full_name": "BAAI/bge-base-en-v1.5",
        "dimension": 768,
        "description": "Faster BGE variant",
    },
    
    # Multilingual models
    "paraphrase-multilingual-mpnet-base-v2": {
        "full_name": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "dimension": 768,
        "description": "Supports 50+ languages",
    },
}


def get_model_info(model_name: str) -> dict:
    """
    Get information about a HuggingFace model
    
    Args:
        model_name: Short name or full name
        
    Returns:
        Model info dict
    """
    # Check if short name
    if model_name in HUGGINGFACE_MODELS:
        return HUGGINGFACE_MODELS[model_name]
    
    # Check if any full name matches
    for short_name, info in HUGGINGFACE_MODELS.items():
        if info["full_name"] == model_name:
            return info
    
    # Unknown model
    return {
        "full_name": model_name,
        "dimension": "unknown",
        "description": "Custom model",
    }


# Testing
if __name__ == "__main__":
    print("Testing HuggingFace Embeddings")
    print("=" * 60)
    
    # Test with fast model
    print("\n1. Loading all-MiniLM-L6-v2 (384 dim)...")
    service = HuggingFaceEmbeddingService("sentence-transformers/all-MiniLM-L6-v2")
    
    print(f"   Dimension: {service.get_dimension()}")
    
    # Generate embeddings
    texts = [
        "Machine learning is fascinating",
        "Neural networks are powerful",
        "Python is a great programming language",
    ]
    
    print(f"\n2. Generating embeddings for {len(texts)} texts...")
    embeddings = service.embed_texts(texts)
    
    print(f"   Generated {len(embeddings)} embeddings")
    print(f"   First embedding: {embeddings[0][:5]}... (showing first 5 values)")
    
    # Calculate similarity
    def cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b)
    
    print(f"\n3. Similarity scores:")
    print(f"   Text 1 vs Text 2: {cosine_sim(embeddings[0], embeddings[1]):.3f}")
    print(f"   Text 1 vs Text 3: {cosine_sim(embeddings[0], embeddings[2]):.3f}")
    print(f"   Text 2 vs Text 3: {cosine_sim(embeddings[1], embeddings[2]):.3f}")
    
    print("\n✅ Test complete!")
