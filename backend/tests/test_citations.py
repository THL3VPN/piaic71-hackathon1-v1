"""
Tests for citation formatting and handling functionality.
"""
import pytest
from app.utils.citation_formatter import format_citations_from_chunks, format_single_citation, validate_citation_format, merge_citations


def test_format_citations_from_chunks():
    """Test formatting citations from retrieved chunks."""
    from app.utils.citation_formatter import format_citations_from_chunks

    chunks = [
        {
            'content': 'This is the first chunk content.',
            'metadata': {
                'source_path': '/book/docs/chapter1.md',
                'title': 'Chapter 1: Introduction',
                'chunk_index': 0
            }
        },
        {
            'content': 'This is the second chunk content.',
            'metadata': {
                'source_path': '/book/docs/chapter2.md',
                'title': 'Chapter 2: Advanced Concepts',
                'chunk_index': 1
            }
        }
    ]

    citations = format_citations_from_chunks(chunks)

    assert len(citations) == 2

    # Check first citation
    first_citation = citations[0]
    assert first_citation['source_path'] == '/book/docs/chapter1.md'
    assert first_citation['title'] == 'Chapter 1: Introduction'
    assert first_citation['chunk_index'] == 0
    assert 'first chunk content' in first_citation['snippet']

    # Check second citation
    second_citation = citations[1]
    assert second_citation['source_path'] == '/book/docs/chapter2.md'
    assert second_citation['title'] == 'Chapter 2: Advanced Concepts'
    assert second_citation['chunk_index'] == 1
    assert 'second chunk content' in second_citation['snippet']


def test_format_single_citation():
    """Test formatting a single citation from a chunk."""
    from app.utils.citation_formatter import format_single_citation

    chunk = {
        'content': 'This is a sample chunk with important information that should be cited properly.',
        'metadata': {
            'source_path': '/book/docs/concepts.md',
            'title': 'Key Concepts',
            'chunk_index': 5
        }
    }

    citation = format_single_citation(chunk)

    assert citation['source_path'] == '/book/docs/concepts.md'
    assert citation['title'] == 'Key Concepts'
    assert citation['chunk_index'] == 5
    assert 'sample chunk with important' in citation['snippet']


def test_format_citation_with_long_content():
    """Test formatting citation with long content (should be truncated)."""
    from app.utils.citation_formatter import format_single_citation

    long_content = 'This is a very long content string that exceeds the typical snippet length. ' * 10
    chunk = {
        'content': long_content,
        'metadata': {
            'source_path': '/book/docs/long-content.md',
            'title': 'Long Content Document',
            'chunk_index': 2
        }
    }

    citation = format_single_citation(chunk)

    # The snippet should be truncated to about 100 characters + '...'
    assert len(citation['snippet']) <= 105  # 100 + '...'
    assert citation['snippet'].endswith('...')


def test_format_citation_with_short_content():
    """Test formatting citation with short content (should not be truncated)."""
    from app.utils.citation_formatter import format_single_citation

    short_content = 'Short content'
    chunk = {
        'content': short_content,
        'metadata': {
            'source_path': '/book/docs/short.md',
            'title': 'Short Document',
            'chunk_index': 0
        }
    }

    citation = format_single_citation(chunk)

    # The snippet should be the full content since it's short
    assert citation['snippet'] == short_content


def test_validate_citation_format_valid():
    """Test validation of properly formatted citations."""
    from app.utils.citation_formatter import validate_citation_format

    valid_citation = {
        'source_path': '/book/docs/chapter.md',
        'title': 'Chapter Title',
        'chunk_index': 1,
        'snippet': 'Content snippet'
    }

    assert validate_citation_format(valid_citation) is True


def test_validate_citation_format_invalid():
    """Test validation of improperly formatted citations."""
    from app.utils.citation_formatter import validate_citation_format

    # Missing required field
    invalid_citation = {
        'source_path': '/book/docs/chapter.md',
        'title': 'Chapter Title',
        'chunk_index': 1
        # Missing 'snippet'
    }

    assert validate_citation_format(invalid_citation) is False

    # Empty citation
    assert validate_citation_format({}) is False

    # None citation
    assert validate_citation_format(None) is False


def test_merge_citations_no_duplicates():
    """Test merging citations without duplicates."""
    existing_citations = [
        {
            'source_path': '/book/docs/chapter1.md',
            'title': 'Chapter 1',
            'chunk_index': 0,
            'snippet': 'First chapter content'
        }
    ]

    new_citations = [
        {
            'source_path': '/book/docs/chapter2.md',
            'title': 'Chapter 2',
            'chunk_index': 0,
            'snippet': 'Second chapter content'
        }
    ]

    merged = merge_citations(existing_citations, new_citations)

    assert len(merged) == 2
    assert merged[0]['source_path'] == '/book/docs/chapter1.md'
    assert merged[1]['source_path'] == '/book/docs/chapter2.md'


def test_merge_citations_with_duplicates():
    """Test merging citations with duplicates (should be removed)."""
    existing_citations = [
        {
            'source_path': '/book/docs/chapter1.md',
            'title': 'Chapter 1',
            'chunk_index': 0,
            'snippet': 'First chapter content'
        }
    ]

    new_citations = [
        {
            'source_path': '/book/docs/chapter1.md',  # Same path
            'title': 'Chapter 1',
            'chunk_index': 0,  # Same index
            'snippet': 'First chapter content'
        }
    ]

    merged = merge_citations(existing_citations, new_citations)

    # Should only have one citation since they're duplicates
    assert len(merged) == 1
    assert merged[0]['source_path'] == '/book/docs/chapter1.md'


def test_merge_citations_same_path_different_index():
    """Test merging citations with same path but different indices (should be kept)."""
    existing_citations = [
        {
            'source_path': '/book/docs/chapter1.md',
            'title': 'Chapter 1',
            'chunk_index': 0,
            'snippet': 'First part of chapter'
        }
    ]

    new_citations = [
        {
            'source_path': '/book/docs/chapter1.md',  # Same path
            'title': 'Chapter 1',
            'chunk_index': 1,  # Different index
            'snippet': 'Second part of chapter'
        }
    ]

    merged = merge_citations(existing_citations, new_citations)

    # Should have both citations since they have different indices
    assert len(merged) == 2
    assert merged[0]['chunk_index'] == 0
    assert merged[1]['chunk_index'] == 1


def test_format_citations_empty_chunks():
    """Test formatting citations from empty chunks list."""
    citations = format_citations_from_chunks([])
    assert citations == []


def test_format_citations_missing_metadata():
    """Test formatting citations when chunks have missing metadata."""
    chunks = [
        {
            'content': 'Content without metadata',
            # No metadata field
        }
    ]

    citations = format_citations_from_chunks(chunks)

    assert len(citations) == 1
    citation = citations[0]
    assert citation['source_path'] == ''
    assert citation['title'] == ''
    assert citation['chunk_index'] == 0  # Default value
    assert 'Content without metadata' in citation['snippet']


def test_format_citations_partial_metadata():
    """Test formatting citations with partial metadata."""
    chunks = [
        {
            'content': 'Content with partial metadata',
            'metadata': {
                'source_path': '/book/docs/partial.md'
                # Missing title and chunk_index
            }
        }
    ]

    citations = format_citations_from_chunks(chunks)

    assert len(citations) == 1
    citation = citations[0]
    assert citation['source_path'] == '/book/docs/partial.md'
    assert citation['title'] == ''  # Default value
    assert citation['chunk_index'] == 0  # Default value
    assert 'partial metadata' in citation['snippet']


def test_format_citations_special_characters():
    """Test formatting citations with special characters in metadata."""
    chunks = [
        {
            'content': 'Content with special characters: émojis and symbøls!',
            'metadata': {
                'source_path': '/book/docs/special-chars.md',
                'title': 'Special Characters & Symbols: A Study',
                'chunk_index': 42
            }
        }
    ]

    citations = format_citations_from_chunks(chunks)

    assert len(citations) == 1
    citation = citations[0]
    assert citation['source_path'] == '/book/docs/special-chars.md'
    assert citation['title'] == 'Special Characters & Symbols: A Study'
    assert citation['chunk_index'] == 42
    assert 'special characters' in citation['snippet'].lower()


def test_merge_citations_large_sets():
    """Test merging large sets of citations."""
    existing_citations = []
    for i in range(10):
        existing_citations.append({
            'source_path': f'/book/docs/chapter{i}.md',
            'title': f'Chapter {i}',
            'chunk_index': 0,
            'snippet': f'Content for chapter {i}'
        })

    new_citations = []
    for i in range(5, 15):  # Overlapping with existing
        new_citations.append({
            'source_path': f'/book/docs/chapter{i}.md',
            'title': f'Chapter {i}',
            'chunk_index': 0,
            'snippet': f'Content for chapter {i}'
        })

    merged = merge_citations(existing_citations, new_citations)

    # Should have 15 unique citations (chapters 0-14)
    assert len(merged) == 15

    # Verify all expected chapters are present
    paths = [c['source_path'] for c in merged]
    for i in range(15):
        expected_path = f'/book/docs/chapter{i}.md'
        assert expected_path in paths