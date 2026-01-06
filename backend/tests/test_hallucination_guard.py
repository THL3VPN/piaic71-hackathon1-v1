"""
Tests for hallucination prevention functionality.
"""
import pytest
from app.utils.hallucination_guard import HallucinationGuard


def test_insufficient_context_detection():
    """Test detection of insufficient context for answering."""
    guard = HallucinationGuard()

    # Test with empty context
    empty_context = ""
    assert guard.is_context_insufficient(empty_context) == True

    # Test with very short context
    short_context = "Short."
    assert guard.is_context_insufficient(short_context) == True

    # Test with sufficient context
    sufficient_context = "This is a more substantial context with adequate information for forming a response."
    assert guard.is_context_insufficient(sufficient_context) == False


def test_low_confidence_result_detection():
    """Test detection of low confidence retrieval results."""
    guard = HallucinationGuard()

    # Test with low confidence results
    low_conf_results = [
        {'score': 0.1, 'content': 'content1'},
        {'score': 0.2, 'content': 'content2'}
    ]
    assert guard.has_low_confidence_results(low_conf_results, threshold=0.5) == True

    # Test with high confidence results
    high_conf_results = [
        {'score': 0.8, 'content': 'content1'},
        {'score': 0.9, 'content': 'content2'}
    ]
    assert guard.has_low_confidence_results(high_conf_results, threshold=0.5) == False

    # Test with mixed confidence results
    mixed_conf_results = [
        {'score': 0.8, 'content': 'content1'},
        {'score': 0.1, 'content': 'content2'}
    ]
    assert guard.has_low_confidence_results(mixed_conf_results, threshold=0.5) == True


def test_answer_grounding_check():
    """Test checking if an answer is properly grounded in provided context."""
    guard = HallucinationGuard()

    context = "The sky is blue. Water freezes at 0°C. The sun rises in the east."
    grounded_answer = "The sky appears blue due to atmospheric scattering."
    non_grounded_answer = "Mars has two moons named Phobos and Deimos."

    # This is a simplified check - in reality, this would involve more sophisticated NLP
    assert guard.is_answer_properly_grounded(grounded_answer, context) == True
    assert guard.is_answer_properly_grounded(non_grounded_answer, context) == False


def test_refusal_response_generation():
    """Test generation of appropriate refusal responses."""
    guard = HallucinationGuard()

    refusal_response = guard.generate_refusal_response("insufficient_context")
    assert refusal_response is not None
    assert "insufficient" in refusal_response.lower() or "unable" in refusal_response.lower()

    refusal_response = guard.generate_refusal_response("low_confidence")
    assert refusal_response is not None
    assert "confidence" in refusal_response.lower() or "unsure" in refusal_response.lower()


def test_hallucination_prevention_end_to_end():
    """Test end-to-end hallucination prevention workflow."""
    guard = HallucinationGuard()

    # Scenario 1: Insufficient context
    context = ""
    question = "What is the capital of France?"

    is_insufficient = guard.is_context_insufficient(context)
    assert is_insufficient == True

    # Scenario 2: Low confidence results
    low_conf_results = [{'score': 0.1, 'content': 'random'}]
    has_low_conf = guard.has_low_confidence_results(low_conf_results)
    assert has_low_conf == True

    # Scenario 3: Proper grounding check
    good_context = "Paris is the capital of France."
    good_answer = "Paris is the capital of France."
    is_properly_grounded = guard.is_answer_properly_grounded(good_answer, good_context)
    assert is_properly_grounded == True


def test_edge_cases():
    """Test edge cases for hallucination prevention."""
    guard = HallucinationGuard()

    # Test with None values
    assert guard.is_context_insufficient(None) == True
    assert guard.has_low_confidence_results(None) == True

    # Test with empty lists
    assert guard.has_low_confidence_results([]) == True

    # Test with special characters
    context_with_symbols = "The formula is H₂O & CO₂ exist."
    answer_with_symbols = "Water has the formula H₂O."
    is_grounded = guard.is_answer_properly_grounded(answer_with_symbols, context_with_symbols)
    # This might be False depending on implementation, but shouldn't crash
    assert isinstance(is_grounded, bool)


def test_confidence_threshold_customization():
    """Test customization of confidence thresholds."""
    guard = HallucinationGuard()

    results = [{'score': 0.6, 'content': 'test'}]

    # With default threshold (would typically be 0.5)
    has_low_conf = guard.has_low_confidence_results(results)
    assert has_low_conf == False  # 0.6 > 0.5

    # With custom lower threshold
    has_low_conf = guard.has_low_confidence_results(results, threshold=0.7)
    assert has_low_conf == True  # 0.6 < 0.7

    # With custom higher threshold
    has_low_conf = guard.has_low_confidence_results(results, threshold=0.5)
    assert has_low_conf == False  # 0.6 > 0.5