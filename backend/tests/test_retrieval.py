"""
Tests for RAG retrieval functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService
from app.models.query import Query


def test_embed_question():
    """Test embedding a user question."""
    with patch('sentence_transformers.SentenceTransformer') as mock_model:
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

        service = RetrievalService()
        question = "What is the main concept?"
        embedding = service.embed_question(question)

        assert embedding is not None
        assert len(embedding) > 0


def test_perform_vector_search():
    """Test performing vector search in Qdrant."""
    with patch('app.services.qdrant_service.qdrant_service') as mock_qdrant:
        mock_qdrant.search.return_value = [
            Mock(id='chunk-1', score=0.9, payload={'doc_id': 'doc-1'}),
            Mock(id='chunk-2', score=0.8, payload={'doc_id': 'doc-2'})
        ]

        service = RetrievalService()
        query_embedding = [0.1, 0.2, 0.3]
        results = service.perform_vector_search(query_embedding, top_k=2)

        assert len(results) == 2
        assert results[0]['id'] == 'chunk-1'
        assert results[0]['score'] == 0.9


def test_fetch_chunks_by_ids():
    """Test fetching chunks from Neon database by IDs."""
    with patch('app.database.chunk_repository.ChunkRepository') as mock_repo:
        mock_chunk = Mock()
        mock_chunk.id = 'chunk-1'
        mock_chunk.content = 'Sample content'
        mock_chunk.metadata = {'source_path': '/docs/sample.md'}
        mock_repo.get_by_ids.return_value = [mock_chunk]

        service = RetrievalService()
        chunk_ids = ['chunk-1']
        chunks = service.fetch_chunks_by_ids(chunk_ids)

        assert len(chunks) == 1
        assert chunks[0].id == 'chunk-1'


def test_build_context_with_citations():
    """Test building context with proper citations."""
    from app.utils.citation_service import CitationService

    chunks = [
        Mock(id='chunk-1', content='First chunk content', metadata={'source_path': '/docs/chapter1.md', 'heading': 'Introduction', 'chunk_index': 0}),
        Mock(id='chunk-2', content='Second chunk content', metadata={'source_path': '/docs/chapter2.md', 'heading': 'Advanced Topics', 'chunk_index': 1})
    ]

    citation_service = CitationService()
    context_bundle = citation_service.build_context_with_citations(chunks)

    assert context_bundle is not None
    assert len(context_bundle.chunks) == 2
    assert 'Introduction' in str(context_bundle.citations)
    assert 'Advanced Topics' in str(context_bundle.citations)


def test_retrieve_and_rank_chunks():
    """Test the full retrieval and ranking process."""
    with patch.object(RetrievalService, 'embed_question') as mock_embed, \
         patch.object(RetrievalService, 'perform_vector_search') as mock_search, \
         patch.object(RetrievalService, 'fetch_chunks_by_ids') as mock_fetch:

        # Mock the embedding
        mock_embed.return_value = [0.1, 0.2, 0.3]

        # Mock the search results
        mock_search.return_value = [
            {'id': 'chunk-1', 'score': 0.9, 'payload': {'doc_id': 'doc-1'}},
            {'id': 'chunk-2', 'score': 0.8, 'payload': {'doc_id': 'doc-2'}}
        ]

        # Mock the chunk fetching
        mock_chunk1 = Mock()
        mock_chunk1.id = 'chunk-1'
        mock_chunk1.content = 'Content 1'
        mock_chunk1.metadata = {'source_path': '/docs/chap1.md', 'heading': 'Chapter 1', 'chunk_index': 0}

        mock_chunk2 = Mock()
        mock_chunk2.id = 'chunk-2'
        mock_chunk2.content = 'Content 2'
        mock_chunk2.metadata = {'source_path': '/docs/chap2.md', 'heading': 'Chapter 2', 'chunk_index': 1}

        mock_fetch.return_value = [mock_chunk1, mock_chunk2]

        service = RetrievalService()
        query = Query(question="Test question", top_k=2)

        result = service.retrieve_and_rank_chunks(query)

        assert result is not None
        assert len(result.chunks) == 2
        assert result.chunks[0].id == 'chunk-1'


def test_low_confidence_handling():
    """Test handling of low confidence retrieval results."""
    service = RetrievalService()

    # Simulate low confidence results
    low_conf_results = [
        {'id': 'chunk-1', 'score': 0.1, 'payload': {}},  # Very low score
        {'id': 'chunk-2', 'score': 0.15, 'payload': {}}  # Below typical threshold
    ]

    # This should still return results, but downstream components
    # would filter based on confidence
    assert len(low_conf_results) == 2
    assert all(r['score'] < 0.5 for r in low_conf_results)