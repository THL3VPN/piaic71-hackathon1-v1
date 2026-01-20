"""
Retrieval service for the RAG system.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
import numpy as np
from app.models.chunk import Chunk
from app.database.chunk_repository import ChunkRepository
from app.services.qdrant_service import qdrant_service
from app.config import settings


class RetrievalService:
    """
    Service class for handling document retrieval operations.
    """

    def __init__(self, db: Session = None):
        """
        Initialize the retrieval service.

        Args:
            db: Database session (optional, can be set later)
        """
        self.db = db
        self.chunk_repository = ChunkRepository(db) if db else None

    def embed_question(self, question: str) -> List[float]:
        """
        Convert a question string to its embedding vector.

        Args:
            question: The question to embed

        Returns:
            Embedding vector as a list of floats
        """
        from .embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        return embedding_service.embed_text(question)

    def perform_vector_search(self, query_vector: List[float], top_k: int = None) -> List[dict]:
        """
        Perform vector similarity search in Qdrant with fallback to database search.

        Args:
            query_vector: The query embedding vector
            top_k: Number of top results to return (defaults to configured value)

        Returns:
            List of search results with chunk IDs and similarity scores
        """
        if top_k is None:
            top_k = settings.top_k

        # First, try to search in Qdrant
        try:
            search_results = qdrant_service.search_similar(
                query_vector=query_vector,
                limit=top_k
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    'id': result['chunk_id'],
                    'score': result['score'],
                    'payload': result.get('payload', {})
                })

            # If we found results in Qdrant, return them
            if formatted_results:
                return formatted_results

        except Exception as e:
            # If Qdrant search fails, log the error and fall back to database search
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Qdrant search failed: {e}. Falling back to database similarity search.")

        # Fall back to database similarity search
        return self._perform_database_similarity_search(query_vector, top_k)

    def _perform_database_similarity_search(self, query_vector: List[float], top_k: int) -> List[dict]:
        """
        Perform similarity search using vectors stored in the database.

        Args:
            query_vector: The query embedding vector
            top_k: Number of top results to return

        Returns:
            List of search results with chunk IDs and similarity scores
        """
        import json
        import numpy as np

        # Get all chunks that have vectors stored in the database
        all_chunks = self.chunk_repository.get_all()

        scored_results = []
        query_array = np.array(query_vector)

        for chunk in all_chunks:
            if chunk.vector:  # Only process chunks that have vectors
                try:
                    # Deserialize the vector from JSON string
                    chunk_vector = json.loads(chunk.vector)
                    chunk_array = np.array(chunk_vector)

                    # Calculate cosine similarity
                    dot_product = np.dot(query_array, chunk_array)
                    norm_query = np.linalg.norm(query_array)
                    norm_chunk = np.linalg.norm(chunk_array)

                    if norm_query != 0 and norm_chunk != 0:
                        similarity = dot_product / (norm_query * norm_chunk)

                        # Create result with required fields
                        result = {
                            'id': str(chunk.id),
                            'score': float(similarity),
                            'payload': {
                                'document_id': str(chunk.document_id),
                                'source_path': '',  # source_path may not be available directly
                                'title': '',  # title may not be available directly
                                'chunk_index': chunk.chunk_index,
                                'content': chunk.chunk_text
                            }
                        }
                        scored_results.append(result)
                except Exception:
                    # Skip chunks with malformed vectors
                    continue

        # Sort by similarity score in descending order
        scored_results.sort(key=lambda x: x['score'], reverse=True)

        # Return top_k results
        return scored_results[:top_k]

    def fetch_chunks_by_ids(self, chunk_ids: List[str]) -> List[Chunk]:
        """
        Fetch chunks from the database by their IDs.

        Args:
            chunk_ids: List of chunk IDs to retrieve

        Returns:
            List of Chunk objects
        """
        if not self.chunk_repository:
            raise ValueError("Database session not provided to retrieval service")

        # Convert string IDs to UUIDs and fetch individually
        import uuid
        chunks = []
        for chunk_id in chunk_ids:
            chunk_uuid = uuid.UUID(chunk_id) if isinstance(chunk_id, str) else chunk_id
            chunk = self.chunk_repository.get_by_id(chunk_uuid)
            if chunk:
                chunks.append(chunk)
        return chunks

    def has_low_confidence_results(self, results: List[dict], threshold: float = None) -> bool:
        """
        Check if retrieval results have low confidence scores.

        Args:
            results: List of retrieval results
            threshold: Confidence threshold (defaults to configured value)

        Returns:
            True if results have low confidence, False otherwise
        """
        if threshold is None:
            threshold = settings.similarity_threshold

        if not results:
            return True  # Empty results = low confidence

        # Check if any result has confidence above threshold
        for result in results:
            if result.get('score', 0) >= threshold:
                return False

        return True

    def retrieve_and_rank_chunks(self, question: str, top_k: int = None, similarity_threshold: float = None) -> List[Chunk]:
        """
        Complete retrieval pipeline: embed question, search, fetch chunks.

        Args:
            question: The question to retrieve relevant chunks for
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score threshold

        Returns:
            List of relevant chunks
        """
        if not self.db or not self.chunk_repository:
            raise ValueError("Database session not provided to retrieval service")

        # Embed the question
        query_vector = self.embed_question(question)

        # Perform vector search
        search_results = self.perform_vector_search(query_vector, top_k)

        # Check confidence threshold
        if self.has_low_confidence_results(search_results, similarity_threshold):
            # Return empty list if confidence is too low
            return []

        # Extract chunk IDs
        chunk_ids = [result['id'] for result in search_results]

        # Fetch chunks from database
        chunks = self.fetch_chunks_by_ids(chunk_ids)

        return chunks