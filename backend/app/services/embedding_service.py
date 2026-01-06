"""
Embedding service for the RAG system.
"""
from typing import List
import numpy as np
from app.config import settings


class EmbeddingService:
    """
    Service class for handling text embedding operations.
    """

    def __init__(self):
        """
        Initialize the embedding service.
        In a real implementation, this would initialize the embedding model.
        """
        self.model = None  # Would be initialized with actual embedding model in production
        self.vector_size = settings.vector_size

    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        # In a real implementation, this would call the embedding model
        # For now, return a placeholder vector of the correct size
        # In practice, this would be something like:
        # return self.model.encode(text).tolist()

        # Generate a deterministic vector based on text content for consistent results
        # This is a placeholder implementation
        text_hash = hash(text) % (2**32)
        vector = []
        for i in range(self.vector_size):
            # Create a pseudo-random but deterministic value based on text and position
            val = ((text_hash * (i + 1)) % 10000) / 10000.0  # Normalize to [0, 1]
            val = (val * 2) - 1  # Normalize to [-1, 1]
            vector.append(val)

        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple texts to embedding vectors.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed_text(text) for text in texts]

    def normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize a vector to unit length.

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        vec_array = np.array(vector)
        norm = np.linalg.norm(vec_array)
        if norm == 0:
            return vector
        normalized = vec_array / norm
        return normalized.tolist()

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score
        """
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)

        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))