"""
Tests for citation formatting functionality.
"""
import pytest
from app.services.citation_service import CitationService


def test_basic_citation_formatting():
    """Test basic citation formatting with source_path, heading, and chunk_index."""
    citation_service = CitationService()

    # Test with all required fields
    source_path = "/book/docs/introduction.md"
    heading = "Introduction to AI"
    chunk_index = 2

    formatted_citation = citation_service.format_citation(source_path, heading, chunk_index)

    assert source_path in formatted_citation
    assert heading in formatted_citation
    assert str(chunk_index) in formatted_citation


def test_citation_with_special_characters():
    """Test citation formatting with special characters in paths and headings."""
    citation_service = CitationService()

    # Test with special characters in path
    source_path = "/book/docs/advanced-topics/vision-and-action.md"
    heading = "Vision & Action: Advanced Models"
    chunk_index = 5

    formatted_citation = citation_service.format_citation(source_path, heading, chunk_index)

    assert source_path in formatted_citation
    assert "Vision & Action" in formatted_citation
    assert str(chunk_index) in formatted_citation


def test_citation_with_numeric_path_components():
    """Test citation formatting with numeric components in paths."""
    citation_service = CitationService()

    source_path = "/book/docs/section-1/subsection-2/content.md"
    heading = "Section 1: Overview"
    chunk_index = 0

    formatted_citation = citation_service.format_citation(source_path, heading, chunk_index)

    assert "section-1" in formatted_citation
    assert "subsection-2" in formatted_citation
    assert str(chunk_index) in formatted_citation


def test_multiple_citation_formatting():
    """Test formatting multiple citations."""
    citation_service = CitationService()

    citations_data = [
        ("/book/docs/chapter1.md", "Getting Started", 0),
        ("/book/docs/chapter2.md", "Advanced Concepts", 1),
        ("/book/docs/chapter3.md", "Implementation Guide", 3)
    ]

    formatted_citations = []
    for source_path, heading, chunk_index in citations_data:
        formatted_citations.append(citation_service.format_citation(source_path, heading, chunk_index))

    assert len(formatted_citations) == 3
    for i, citation in enumerate(formatted_citations):
        assert citations_data[i][0] in citation  # source_path
        assert citations_data[i][1] in citation  # heading
        assert str(citations_data[i][2]) in citation  # chunk_index


def test_citation_edge_cases():
    """Test citation formatting with edge cases."""
    citation_service = CitationService()

    # Test with empty heading
    citation1 = citation_service.format_citation("/book/docs/test.md", "", 1)
    assert "/book/docs/test.md" in citation1
    assert "1" in citation1

    # Test with long path
    long_path = "/book/docs/module/submodule/subsubmodule/very/long/path/to/document.md"
    citation2 = citation_service.format_citation(long_path, "Long Path Doc", 0)
    assert "document.md" in citation2  # Should contain the actual document name
    assert "Long Path Doc" in citation2

    # Test with zero chunk index
    citation3 = citation_service.format_citation("/book/docs/start.md", "Start", 0)
    assert "0" in citation3

    # Test with large chunk index
    citation4 = citation_service.format_citation("/book/docs/end.md", "End", 999)
    assert "999" in citation4


def test_citation_consistency():
    """Test that same inputs always produce same citation format."""
    citation_service = CitationService()

    # Same inputs should always produce the same output
    citation1 = citation_service.format_citation("/book/docs/test.md", "Test Heading", 5)
    citation2 = citation_service.format_citation("/book/docs/test.md", "Test Heading", 5)
    citation3 = citation_service.format_citation("/book/docs/test.md", "Test Heading", 5)

    assert citation1 == citation2 == citation3


def test_citation_format_completeness():
    """Test that all required citation elements are included in the formatted citation."""
    citation_service = CitationService()

    source_path = "/book/docs/conceptual-framework.md"
    heading = "Conceptual Framework"
    chunk_index = 12

    formatted_citation = citation_service.format_citation(source_path, heading, chunk_index)

    # Verify all elements are present
    assert source_path in formatted_citation
    assert heading in formatted_citation
    assert str(chunk_index) in formatted_citation

    # Verify the citation is properly structured (not just concatenating)
    # The format should be meaningful, not just raw concatenation
    assert len(formatted_citation) > len(source_path + heading + str(chunk_index))


def test_citation_format_readability():
    """Test that citations are human-readable and well-formatted."""
    citation_service = CitationService()

    test_cases = [
        ("/book/docs/getting-started.md", "Getting Started", 0),
        ("/book/docs/advanced/transformers.mdx", "Transformer Architecture", 7),
        ("/book/docs/conclusion.md", "Conclusion and Future Work", 15)
    ]

    for source_path, heading, chunk_index in test_cases:
        citation = citation_service.format_citation(source_path, heading, chunk_index)

        # Citations should be readable - not just a jumbled string
        # They should have some structure/punctuation
        assert len(citation) > 0
        assert len(citation.split()) > 2  # Should have multiple words/terms


def test_citation_with_encoded_characters():
    """Test citation formatting with URL-encoded or special characters."""
    citation_service = CitationService()

    # Test with encoded characters that might appear in paths
    source_path = "/book/docs/path-with-%20space.md"
    heading = "Path with Space"
    chunk_index = 1

    citation = citation_service.format_citation(source_path, heading, chunk_index)

    # Should handle encoded characters appropriately
    assert "path-with-" in citation
    assert str(chunk_index) in citation