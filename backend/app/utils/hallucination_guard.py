"""
Hallucination prevention utilities for the RAG system.
"""
from typing import List, Dict, Any, Optional
import logging


logger = logging.getLogger(__name__)


class HallucinationGuard:
    """
    Utility class for preventing hallucination in RAG responses.
    """

    def __init__(self, confidence_threshold: float = None):
        """
        Initialize the hallucination guard.

        Args:
            confidence_threshold: Minimum confidence score for accepting results (defaults to configured value)
        """
        from app.config import settings
        self.confidence_threshold = confidence_threshold or settings.similarity_threshold

    def is_context_insufficient(self, context: str, min_length: int = 10) -> bool:
        """
        Check if the provided context is insufficient for generating a response.

        Args:
            context: The context to evaluate
            min_length: Minimum length of context to be considered sufficient

        Returns:
            True if context is insufficient, False otherwise
        """
        if not context:
            return True

        # Check if context has enough content
        clean_context = context.strip()
        if len(clean_context) < min_length:
            return True

        return False

    def has_low_confidence_results(self, results: List[Dict[str, Any]], threshold: float = None) -> bool:
        """
        Check if retrieval results have low confidence scores.

        Args:
            results: List of retrieval results with scores (can be dicts or Chunk objects)
            threshold: Confidence threshold (uses default if not provided)

        Returns:
            True if results have low confidence, False otherwise
        """
        if threshold is None:
            threshold = self.confidence_threshold

        if not results:
            return True  # No results = low confidence

        # Check if any result meets the confidence threshold
        for result in results:
            # Handle both dictionary results and Chunk objects
            if isinstance(result, dict):
                score = result.get('score', 0)
            else:
                # If it's a Chunk object, we can't determine its similarity score
                # This case shouldn't normally happen if the retrieval service works correctly
                # but we handle it for robustness
                score = 0  # Assume low confidence for Chunk objects

            if score >= threshold:
                return False  # Found at least one high-confidence result

        return True  # All results are below threshold

    def is_answer_properly_grounded(self, answer: str, context: str) -> bool:
        """
        Check if an answer is properly grounded in the provided context.

        Args:
            answer: The answer to check
            context: The context that should support the answer

        Returns:
            True if answer is properly grounded, False otherwise
        """
        if not answer or not context:
            return False

        # This is a simplified check - in practice, this would involve more sophisticated NLP
        # For now, check if the answer contains content that appears in the context
        answer_lower = answer.lower()
        context_lower = context.lower()

        # Count how many words from the answer appear in the context
        answer_words = set(answer_lower.split())
        context_words = set(context_lower.split())

        if not answer_words:
            return False

        # Calculate overlap ratio
        common_words = answer_words.intersection(context_words)
        overlap_ratio = len(common_words) / len(answer_words)

        # If less than 30% of answer words appear in context, consider it potentially hallucinated
        return overlap_ratio >= 0.3

    def generate_refusal_response(self, reason: str = "insufficient_context") -> str:
        """
        Generate an appropriate refusal response when unable to answer.

        Args:
            reason: Reason for refusal (e.g., "insufficient_context", "low_confidence")

        Returns:
            Appropriate refusal message
        """
        if reason == "insufficient_context":
            return "I don't have sufficient information in the book content to answer this question."
        elif reason == "low_confidence":
            return "The retrieved information doesn't have sufficient confidence to provide a reliable answer."
        else:
            return "I cannot provide an answer based on the available book content."

    def should_refuse_to_answer(self, context: str = None, results: List[Dict[str, Any]] = None,
                                threshold: float = None) -> tuple[bool, str]:
        """
        Determine if the system should refuse to answer based on context and results.

        Args:
            context: Provided context for the answer
            results: Retrieval results
            threshold: Confidence threshold

        Returns:
            Tuple of (should_refuse, reason_for_refusal)
        """
        if threshold is None:
            threshold = self.confidence_threshold

        # Check if context is insufficient
        if self.is_context_insufficient(context):
            return True, "insufficient_context"

        # Check if results have low confidence
        if results and self.has_low_confidence_results(results, threshold):
            return True, "low_confidence"

        return False, ""

    def validate_response_against_context(self, response: str, context: str,
                                         retrieval_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a response against the provided context and retrieval results.

        Args:
            response: The response to validate
            context: The context used to generate the response
            retrieval_results: The retrieval results used

        Returns:
            Validation results with flags and recommendations
        """
        is_grounded = self.is_answer_properly_grounded(response, context)
        is_insufficient_context = self.is_context_insufficient(context)

        has_low_confidence = False
        if retrieval_results:
            has_low_confidence = self.has_low_confidence_results(retrieval_results)

        should_refuse, refusal_reason = self.should_refuse_to_answer(
            context=context,
            results=retrieval_results
        )

        return {
            "is_grounded": is_grounded,
            "has_sufficient_context": not is_insufficient_context,
            "has_high_confidence_results": not has_low_confidence,
            "should_refuse_to_answer": should_refuse,
            "refusal_reason": refusal_reason,
            "validation_passed": is_grounded and not should_refuse
        }


# Global instance for easy access
hallucination_guard = HallucinationGuard()