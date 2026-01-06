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
        # In a real implementation, this would call an embedding model
        # For now, return a placeholder vector of the correct size
        return [0.0] * settings.vector_size

    def perform_vector_search(self, query_vector: List[float], top_k: int = None) -> List[dict]:
        """
        Perform vector similarity search in Qdrant.

        Args:
            query_vector: The query embedding vector
            top_k: Number of top results to return (defaults to configured value)

        Returns:
            List of search results with chunk IDs and similarity scores
        """
        if top_k is None:
            top_k = settings.top_k

        # Perform search in Qdrant
        search_results = qdrant_service.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        # Format results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                'id': result.id,
                'score': result.score,
                'payload': result.payload
            })

        return formatted_results

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
        return self.chunk_repository.get_by_ids(chunk_ids)

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