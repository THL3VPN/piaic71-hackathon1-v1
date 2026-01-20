"""
Citation formatting utilities for the backend service.
"""
from typing import List, Dict, Any
from app.models.chunk import Chunk


def format_citations_from_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format citations from retrieved chunks according to the specification.

    Args:
        chunks: List of retrieved chunks with metadata

    Returns:
        List of properly formatted citation objects
    """
    citations = []
    for chunk in chunks:
        # Extract metadata from the chunk
        metadata = chunk.get('metadata', {})

        citation = {
            'source_path': metadata.get('source_path', ''),
            'title': metadata.get('title', ''),
            'chunk_index': metadata.get('chunk_index', 0),
            'snippet': chunk.get('content', '')[:100] + '...' if len(chunk.get('content', '')) > 100 else chunk.get('content', '')
        }
        citations.append(citation)

    return citations


def format_single_citation(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a single citation from a chunk.

    Args:
        chunk: A single retrieved chunk with metadata

    Returns:
        A properly formatted citation object
    """
    metadata = chunk.get('metadata', {})

    return {
        'source_path': metadata.get('source_path', ''),
        'title': metadata.get('title', ''),
        'chunk_index': metadata.get('chunk_index', 0),
        'snippet': chunk.get('content', '')[:100] + '...' if len(chunk.get('content', '')) > 100 else chunk.get('content', '')
    }


def validate_citation_format(citation: Dict[str, Any]) -> bool:
    """
    Validate that a citation object has the required fields.

    Args:
        citation: Citation object to validate

    Returns:
        True if citation has all required fields, False otherwise
    """
    required_fields = ['source_path', 'title', 'chunk_index', 'snippet']
    return all(field in citation for field in required_fields)


def merge_citations(existing_citations: List[Dict[str, Any]], new_citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge new citations with existing ones, avoiding duplicates.

    Args:
        existing_citations: List of existing citations
        new_citations: List of new citations to add

    Returns:
        Merged list of citations without duplicates
    """
    # Create a set of unique identifiers to avoid duplicates
    existing_keys = {
        f"{cit['source_path']}_{cit['chunk_index']}"
        for cit in existing_citations
    }

    merged = existing_citations.copy()

    for citation in new_citations:
        key = f"{citation['source_path']}_{citation['chunk_index']}"
        if key not in existing_keys:
            merged.append(citation)
            existing_keys.add(key)

    return merged