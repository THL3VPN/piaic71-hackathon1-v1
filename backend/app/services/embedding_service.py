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
        This will initialize the embedding model.
        """
        try:
            from sentence_transformers import SentenceTransformer
            # Force CPU usage to avoid CUDA compatibility issues
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')  # Lightweight model
        except ImportError:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")

        self.vector_size = settings.vector_size

    def embed_text(self, text: str) -> List[float]:
        """
        Convert text to embedding vector.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        if not text.strip():
            # Return zero vector for empty text
            return [0.0] * self.vector_size

        # Use the actual embedding model
        embedding = self.model.encode([text], convert_to_numpy=True)[0]
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple texts to embedding vectors.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Filter out empty texts
        non_empty_texts = [text for text in texts if text.strip()]
        if not non_empty_texts:
            return [[0.0] * self.vector_size] * len(texts)

        # Get embeddings for non-empty texts
        embeddings = self.model.encode(non_empty_texts, convert_to_numpy=True)
        embedding_list = [embedding.tolist() for embedding in embeddings]

        # Handle case where some texts were empty by inserting zero vectors
        result = []
        text_idx = 0
        for text in texts:
            if text.strip():
                result.append(embedding_list[text_idx])
                text_idx += 1
            else:
                result.append([0.0] * self.vector_size)

        return result

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