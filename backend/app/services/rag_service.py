"""
RAG orchestration service.
"""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.citation_service import CitationService
from app.utils.hallucination_guard import hallucination_guard
from app.models.chunk import Chunk
from app.models.document import Document
from app.config import settings


logger = logging.getLogger(__name__)


class RagService:
    """
    Main service class that orchestrates the RAG (Retrieval-Augmented Generation) pipeline.
    """

    def __init__(self, db: Session):
        """
        Initialize the RAG service.

        Args:
            db: Database session
        """
        self.db = db
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService(db)
        self.citation_service = CitationService()
        self.hallucination_guard = hallucination_guard

    def process_query(self, question: str, top_k: int = None, similarity_threshold: float = None) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            question: The user's question
            top_k: Number of top results to retrieve (defaults to configured value)
            similarity_threshold: Minimum similarity score threshold (defaults to configured value)

        Returns:
            Dictionary containing the answer, citations, and metadata
        """
        if top_k is None:
            top_k = settings.top_k
        if similarity_threshold is None:
            similarity_threshold = settings.similarity_threshold

        logger.info(f"Processing query: {question[:50]}...")

        # Step 1: Embed the question
        query_embedding = self.embedding_service.embed_text(question)
        logger.debug(f"Question embedded to {len(query_embedding)}-dimensional vector")

        # Step 2: Retrieve relevant chunks
        retrieved_chunks = self.retrieval_service.retrieve_chunks(
            query_embedding,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        # Step 3: Check if we have sufficient, high-confidence results
        if not retrieved_chunks:
            logger.info("No relevant chunks found for query")
            return {
                "answer": self.hallucination_guard.generate_refusal_response("insufficient_context"),
                "citations": [],
                "retrieved_chunks": [],
                "confidence_score": 0.0,
                "was_refused": True,
                "refusal_reason": "no_relevant_chunks_found"
            }

        # Check if results have sufficient confidence
        max_similarity = max((chunk.metadata or {}).get('similarity_score', 0) for chunk in retrieved_chunks)
        if max_similarity < similarity_threshold:
            logger.info(f"Retrieved chunks have low confidence (max: {max_similarity:.3f} < threshold: {similarity_threshold:.3f})")
            return {
                "answer": self.hallucination_guard.generate_refusal_response("low_confidence"),
                "citations": [],
                "retrieved_chunks": [chunk.to_dict() for chunk in retrieved_chunks],
                "confidence_score": max_similarity,
                "was_refused": True,
                "refusal_reason": "low_confidence_results"
            }

        # Step 4: Build context with citations
        context, citations = self.citation_service.build_context_with_citations(retrieved_chunks)
        logger.debug(f"Built context with {len(retrieved_chunks)} chunks and {len(citations)} citations")

        # Step 5: Validate that the context is sufficient
        if self.hallucination_guard.is_context_insufficient(context):
            logger.info("Context is insufficient despite finding chunks")
            return {
                "answer": self.hallucination_guard.generate_refusal_response("insufficient_context"),
                "citations": citations,
                "retrieved_chunks": [chunk.to_dict() for chunk in retrieved_chunks],
                "confidence_score": max_similarity,
                "was_refused": True,
                "refusal_reason": "insufficient_context_after_retrieval"
            }

        # Step 6: In a real implementation, we would now call the LLM with the context
        # For now, we'll simulate a response based on the context
        answer = self._generate_answer_from_context(question, context)

        # Step 7: Validate the answer is properly grounded in context
        if not self.hallucination_guard.is_answer_properly_grounded(answer, context):
            logger.warning("Generated answer is not properly grounded in context")
            return {
                "answer": self.hallucination_guard.generate_refusal_response("not_properly_grounded"),
                "citations": citations,
                "retrieved_chunks": [chunk.to_dict() for chunk in retrieved_chunks],
                "confidence_score": max_similarity * 0.5,  # Lower confidence due to grounding issues
                "was_refused": True,
                "refusal_reason": "answer_not_properly_grounded"
            }

        logger.info(f"Query processed successfully with {len(retrieved_chunks)} supporting chunks")
        return {
            "answer": answer,
            "citations": citations,
            "retrieved_chunks": [chunk.to_dict() for chunk in retrieved_chunks],
            "confidence_score": max_similarity,
            "was_refused": False,
            "refusal_reason": None
        }

    def _generate_answer_from_context(self, question: str, context: str) -> str:
        """
        Generate an answer based on the question and context.
        This is a placeholder implementation - in production, this would call an LLM.

        Args:
            question: The original question
            context: The context containing relevant information

        Returns:
            Generated answer string
        """
        # In a real implementation, this would call an LLM API with the context
        # For now, we'll create a simple answer based on the context
        return f"Based on the provided context, here is an answer to your question '{question[:50]}...':\n\n{context[:500]}..."

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the retrieval system.

        Returns:
            Dictionary with retrieval statistics
        """
        # This would typically aggregate data from a statistics repository
        # For now, return placeholder values
        return {
            "total_queries_processed": 0,
            "average_response_time": 0.0,
            "average_chunks_retrieved": 0,
            "refusal_rate": 0.0,
            "most_common_refusal_reasons": []
        }

    def validate_query_response(self, question: str, response: str, context: str) -> Dict[str, Any]:
        """
        Validate that a query response is properly grounded and not hallucinated.

        Args:
            question: Original question
            response: Generated response
            context: Context used to generate response

        Returns:
            Validation results
        """
        return self.hallucination_guard.validate_response_against_context(
            response=response,
            context=context
        )


