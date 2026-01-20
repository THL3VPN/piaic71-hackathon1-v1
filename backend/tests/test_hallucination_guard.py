"""
Tests for hallucination prevention functionality.
"""
import pytest
from unittest.mock import Mock, patch
from app.utils.hallucination_guard import HallucinationGuard


def test_insufficient_context_detection():
    """Test detection of insufficient context for response generation."""
    guard = HallucinationGuard()

    # Test with empty context
    assert guard.is_context_insufficient("") is True
    assert guard.is_context_insufficient(None) is True

    # Test with short context (below threshold)
    assert guard.is_context_insufficient("Short", min_length=10) is True

    # Test with sufficient context
    assert guard.is_context_insufficient("This is a sufficiently long context string for testing.", min_length=10) is False


def test_low_confidence_result_detection():
    """Test detection of low confidence retrieval results."""
    guard = HallucinationGuard()

    # Test with low confidence results
    low_conf_results = [
        {'id': 'chunk-1', 'score': 0.1, 'payload': {}},  # Very low score
        {'id': 'chunk-2', 'score': 0.15, 'payload': {}}  # Below typical threshold
    ]
    assert guard.has_low_confidence_results(low_conf_results, threshold=0.5) is True

    # Test with high confidence results
    high_conf_results = [
        {'id': 'chunk-1', 'score': 0.8, 'payload': {}},
        {'id': 'chunk-2', 'score': 0.9, 'payload': {}}
    ]
    assert guard.has_low_confidence_results(high_conf_results, threshold=0.7) is False

    # Test with mixed confidence results
    mixed_conf_results = [
        {'id': 'chunk-1', 'score': 0.8, 'payload': {}},
        {'id': 'chunk-2', 'score': 0.1, 'payload': {}}
    ]
    assert guard.has_low_confidence_results(mixed_conf_results, threshold=0.5) is False  # Has at least one high-confidence result
    assert guard.has_low_confidence_results(mixed_conf_results, threshold=0.9) is True  # No results meet higher threshold


def test_answer_grounding_check():
    """Test checking if an answer is properly grounded in provided context."""
    guard = HallucinationGuard()

    # Test with well-grounded answer
    answer = "The concept is explained in the document as a key principle."
    context = "The concept is explained in the document as a key principle that governs the system."
    assert guard.is_answer_properly_grounded(answer, context) is True

    # Test with ungrounded answer
    answer = "The sky is blue and water is wet."
    context = "The document discusses advanced AI concepts and neural networks."
    assert guard.is_answer_properly_grounded(answer, context) is False

    # Test with partially grounded answer
    answer = "The concept is a key principle, and the sky is blue."
    context = "The document explains that the concept is a key principle."
    # This should be partially grounded (some overlap exists)
    assert guard.is_answer_properly_grounded(answer, context) is True  # Some content overlaps


def test_generate_refusal_response():
    """Test generation of appropriate refusal responses."""
    guard = HallucinationGuard()

    # Test insufficient context reason
    refusal = guard.generate_refusal_response("insufficient_context")
    assert "insufficient" in refusal.lower() or "cannot" in refusal.lower()

    # Test low confidence reason
    refusal = guard.generate_refusal_response("low_confidence")
    assert "confidence" in refusal.lower() or "uncertain" in refusal.lower()

    # Test default reason
    refusal = guard.generate_refusal_response("unknown")
    assert "cannot" in refusal.lower() or "insufficient" in refusal.lower()


def test_refusal_behavior_with_insufficient_information():
    """Test the refusal behavior when no context is available."""
    guard = HallucinationGuard()

    # Test with empty context
    should_refuse, reason = guard.should_refuse_to_answer(context="", results=[])
    assert should_refuse is True

    # Test with None context
    should_refuse, reason = guard.should_refuse_to_answer(context=None, results=[])
    assert should_refuse is True

    # Test with low confidence results
    low_conf_results = [{'id': 'chunk-1', 'score': 0.1}]
    should_refuse, reason = guard.should_refuse_to_answer(context="some context", results=low_conf_results, threshold=0.5)
    assert should_refuse is True
    assert reason == "low_confidence"


def test_refusal_behavior_with_sufficient_information():
    """Test that refusal doesn't happen when sufficient information is available."""
    guard = HallucinationGuard()

    # Test with good context and high confidence results
    context = "This is a good context string with sufficient information."
    high_conf_results = [{'id': 'chunk-1', 'score': 0.8}]

    should_refuse, reason = guard.should_refuse_to_answer(context=context, results=high_conf_results, threshold=0.5)
    assert should_refuse is False
    assert reason == ""


def test_validation_against_context():
    """Test the complete validation against context functionality."""
    guard = HallucinationGuard()

    # Test with properly grounded response
    response = "Based on the document, the concept is a key principle."
    context = "The document explains that the concept is a key principle in the system."
    results = [{'id': 'chunk-1', 'score': 0.8}]

    validation = guard.validate_response_against_context(response, context, results)

    assert validation["is_grounded"] is True
    assert validation["has_sufficient_context"] is True
    assert validation["has_high_confidence_results"] is True
    assert validation["should_refuse_to_answer"] is False
    assert validation["validation_passed"] is True


def test_validation_with_insufficient_elements():
    """Test validation when elements are insufficient."""
    guard = HallucinationGuard()

    # Test with poorly grounded response
    response = "The sky is blue and unrelated to the document."
    context = "The document discusses AI concepts."
    results = [{'id': 'chunk-1', 'score': 0.8}]

    validation = guard.validate_response_against_context(response, context, results)

    assert validation["is_grounded"] is False
    assert validation["validation_passed"] is False


def test_validation_with_low_confidence_results():
    """Test validation when results have low confidence."""
    guard = HallucinationGuard()

    # Test with good grounding but low confidence results
    response = "Based on the document, the concept is important."
    context = "The document explains the concept is important."
    low_conf_results = [{'id': 'chunk-1', 'score': 0.1}]

    validation = guard.validate_response_against_context(response, context, low_conf_results)

    assert validation["has_high_confidence_results"] is False
    assert validation["should_refuse_to_answer"] is True
    assert validation["validation_passed"] is False


def test_validation_with_insufficient_context():
    """Test validation when context is insufficient."""
    guard = HallucinationGuard()

    # Test with insufficient context
    response = "Based on the document..."
    context = ""  # Empty context
    results = [{'id': 'chunk-1', 'score': 0.8}]

    validation = guard.validate_response_against_context(response, context, results)

    assert validation["has_sufficient_context"] is False
    assert validation["should_refuse_to_answer"] is True
    assert validation["validation_passed"] is False


def test_edge_cases():
    """Test edge cases for hallucination prevention."""
    guard = HallucinationGuard()

    # Test with None values
    should_refuse, reason = guard.should_refuse_to_answer(context=None, results=None)
    assert should_refuse is True

    # Test with empty lists
    validation = guard.validate_response_against_context("", "", [])
    assert validation["has_sufficient_context"] is False
    assert validation["has_high_confidence_results"] is False
    assert validation["should_refuse_to_answer"] is True

    # Test with special characters in content
    response_with_symbols = "The formula is H₂O & CO₂ exist in the document."
    context_with_symbols = "The document mentions that H₂O & CO₂ exist in nature."
    results = [{'id': 'chunk-1', 'score': 0.8}]

    # Should handle special characters without crashing
    validation = guard.validate_response_against_context(response_with_symbols, context_with_symbols, results)
    assert isinstance(validation["is_grounded"], bool)


def test_confidence_threshold_customization():
    """Test customization of confidence thresholds."""
    guard = HallucinationGuard()

    results = [{'id': 'chunk-1', 'score': 0.6}]

    # With default threshold (would typically be 0.5)
    has_low_conf = guard.has_low_confidence_results(results)
    assert has_low_conf is False  # 0.6 > 0.5

    # With custom lower threshold
    has_low_conf = guard.has_low_confidence_results(results, threshold=0.7)
    assert has_low_conf is True  # 0.6 < 0.7

    # With custom higher threshold
    has_low_conf = guard.has_low_confidence_results(results, threshold=0.5)
    assert has_low_conf is False  # 0.6 > 0.5


def test_context_overlap_calculation():
    """Test the internal context overlap calculation."""
    guard = HallucinationGuard()

    # Test with complete overlap
    response = "This is the content from the document."
    context = "This is the content from the document."
    overlap_ratio = guard._calculate_context_overlap(response, context)
    assert overlap_ratio >= 0.8  # High overlap

    # Test with no overlap
    response = "This is completely different content."
    context = "The document discusses AI concepts."
    overlap_ratio = guard._calculate_context_overlap(response, context)
    assert overlap_ratio < 0.3  # Low overlap

    # Test with partial overlap
    response = "Based on the document, AI concepts are important."
    context = "The document discusses AI concepts and their importance."
    overlap_ratio = guard._calculate_context_overlap(response, context)
    assert 0.3 <= overlap_ratio <= 0.8  # Moderate overlap