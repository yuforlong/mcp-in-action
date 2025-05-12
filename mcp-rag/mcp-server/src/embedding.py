import numpy as np
from sentence_transformers import SentenceTransformer
import logging

from settings import embedding_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for creating embeddings from text."""
    
    def __init__(self):
        """Initialize the embedding service."""
        logger.info(f"Loading embedding model: {embedding_settings.MODEL}")
        self.model = SentenceTransformer(embedding_settings.MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding model loaded with dimension: {self.dimension}")
    
    def embed(self, text: str) -> np.ndarray:
        """Create an embedding vector from the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector as a numpy array
        """
        if not text:
            # Return a zero vector for empty text
            return np.zeros(self.dimension, dtype=np.float32)
        
        # Create embedding
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.astype(np.float32)
    
    def batch_embed(self, texts: list[str]) -> list[np.ndarray]:
        """Create embedding vectors for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter empty texts
        non_empty_indices = [i for i, text in enumerate(texts) if text]
        non_empty_texts = [texts[i] for i in non_empty_indices]
        
        # Create embeddings for non-empty texts
        if non_empty_texts:
            embeddings = self.model.encode(non_empty_texts, normalize_embeddings=True)
            embeddings = embeddings.astype(np.float32)
        else:
            embeddings = []
        
        # Create result array with zero vectors for empty texts
        result = [np.zeros(self.dimension, dtype=np.float32) for _ in range(len(texts))]
        for idx, embedding_idx in enumerate(non_empty_indices):
            if idx < len(embeddings):
                result[embedding_idx] = embeddings[idx]
        
        return result 