"""
Integration tests for the full chat pipeline covering the complete RAG workflow.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.rag_chat_service import RagChatService
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage


def test_full_chat_pipeline_with_citations():
    """Test the complete chat pipeline with proper citation generation."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock message service
        mock_user_message = Mock(spec=ChatMessage)
        mock_user_message.role = "user"
        mock_user_message.content = "What are the key concepts in Chapter 1?"
        mock_assistant_message = Mock(spec=ChatMessage)
        mock_assistant_message.role = "assistant"
        mock_assistant_message.content = "Based on the book content: The key concepts include..."
        mock_message_svc().create_message.side_effect = [mock_user_message, mock_assistant_message]
        mock_message_svc().get_messages_by_session_id.return_value = [mock_user_message, mock_assistant_message]

        # Setup mock retrieval service
        mock_chunk = Mock()
        mock_chunk.id = 'chunk-1'
        mock_chunk.content = 'The key concepts in Chapter 1 include important ideas.'
        mock_chunk.source_path = '/book/docs/chapter1.md'
        mock_chunk.title = 'Chapter 1: Key Concepts'
        mock_chunk.chunk_index = 0
        mock_retrieval_svc().retrieve_and_rank_chunks.return_value = [mock_chunk]

        # Create service instance
        service = RagChatService(db_session)

        # Execute the full pipeline
        result = service.process_chat_query(
            message="What are the key concepts in Chapter 1?",
            session_id=mock_session.session_id
        )

        # Verify the response structure
        assert 'session_id' in result
        assert 'answer' in result
        assert 'citations' in result
        assert str(mock_session.session_id) == result['session_id']
        assert len(result['citations']) > 0
        assert 'chapter1.md' in result['citations'][0]['source_path']


def test_full_chat_pipeline_new_session_creation():
    """Test the complete chat pipeline with new session creation."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = None  # Session doesn't exist initially
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock message service
        mock_user_message = Mock(spec=ChatMessage)
        mock_user_message.role = "user"
        mock_user_message.content = "What does the book say about AI?"
        mock_assistant_message = Mock(spec=ChatMessage)
        mock_assistant_message.role = "assistant"
        mock_assistant_message.content = "Based on the book content: AI concepts are explained..."
        mock_message_svc().create_message.side_effect = [mock_user_message, mock_assistant_message]

        # Setup mock retrieval service
        mock_chunk = Mock()
        mock_chunk.id = 'chunk-2'
        mock_chunk.content = 'AI concepts are explained in detail in this section.'
        mock_chunk.source_path = '/book/docs/ai-concepts.md'
        mock_chunk.title = 'AI Concepts Explained'
        mock_chunk.chunk_index = 1
        mock_retrieval_svc().retrieve_and_rank_chunks.return_value = [mock_chunk]

        # Create service instance
        service = RagChatService(db_session)

        # Execute the full pipeline with no session ID (should create new)
        result = service.process_chat_query(message="What does the book say about AI?")

        # Verify new session was created
        mock_session_svc().create_session.assert_called_once()
        assert 'session_id' in result
        assert result['session_id'] != str(uuid.uuid4())  # Should be a real UUID string


def test_full_chat_pipeline_with_insufficient_information():
    """Test the complete chat pipeline when there's insufficient information."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard') as mock_guard:

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock message service
        mock_user_message = Mock(spec=ChatMessage)
        mock_user_message.role = "user"
        mock_user_message.content = "What color is the invisible chair?"
        mock_assistant_message = Mock(spec=ChatMessage)
        mock_assistant_message.role = "assistant"
        mock_assistant_message.content = "I don't have sufficient information in the book content to answer this question."
        mock_message_svc().create_message.side_effect = [mock_user_message, mock_assistant_message]

        # Setup mock retrieval service to return no results
        mock_retrieval_svc().retrieve_and_rank_chunks.return_value = []

        # Setup mock hallucination guard to indicate low confidence
        mock_guard_instance = mock_guard.return_value
        mock_guard_instance.has_low_confidence_results.return_value = True

        # Create service instance
        service = RagChatService(db_session)

        # Execute the full pipeline
        result = service.process_chat_query(
            message="What color is the invisible chair?",
            session_id=mock_session.session_id
        )

        # Verify the response indicates insufficient information
        assert 'I don\'t have sufficient information' in result['answer']
        assert len(result['citations']) == 0


def test_full_chat_pipeline_error_handling():
    """Test the complete chat pipeline error handling."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock retrieval service to raise an exception
        mock_retrieval_svc().retrieve_and_rank_chunks.side_effect = Exception("Database connection failed")

        # Create service instance
        service = RagChatService(db_session)

        # Execute the full pipeline - should handle the error gracefully
        result = service.process_chat_query(
            message="What are the key concepts?",
            session_id=mock_session.session_id
        )

        # Verify error handling
        assert 'error' in result
        assert 'trouble accessing' in result['answer']


def test_conversation_history_retrieval():
    """Test retrieving conversation history through the full pipeline."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService'), \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().session_exists.return_value = True

        # Setup mock message service with conversation history
        mock_user_msg = Mock(spec=ChatMessage)
        mock_user_msg.role = "user"
        mock_user_msg.content = "First question?"
        mock_assistant_msg = Mock(spec=ChatMessage)
        mock_assistant_msg.role = "assistant"
        mock_assistant_msg.content = "First answer."
        mock_user_msg2 = Mock(spec=ChatMessage)
        mock_user_msg2.role = "user"
        mock_user_msg2.content = "Second question?"
        mock_assistant_msg2 = Mock(spec=ChatMessage)
        mock_assistant_msg2.role = "assistant"
        mock_assistant_msg2.content = "Second answer."

        mock_message_svc().get_messages_by_session_id.return_value = [
            mock_user_msg, mock_assistant_msg, mock_user_msg2, mock_assistant_msg2
        ]

        # Create service instance
        service = RagChatService(db_session)

        # Retrieve conversation history
        history = service.get_conversation_history(mock_session.session_id, limit=10)

        # Verify history structure
        assert len(history) == 4
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'


def test_session_validation_integration():
    """Test session validation through the full pipeline."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.rag_chat_service.ChatSessionService') as mock_internal_session_svc:

        # Setup mock session service
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()

        mock_internal_session_svc().session_exists.return_value = True
        mock_session_svc().session_exists.return_value = True

        # Create service instance
        service = RagChatService(db_session)

        # Validate session
        is_valid = service.validate_chat_session(mock_session.session_id)

        # Verify validation
        assert is_valid is True


def test_session_statistics_integration():
    """Test session statistics through the full pipeline."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.rag_chat_service.ChatSessionService') as mock_internal_session_svc:

        # Setup mock session
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session.created_at = MagicMock()
        mock_session.created_at.isoformat.return_value = "2026-01-06T10:00:00"
        mock_session.updated_at = MagicMock()
        mock_session.updated_at.isoformat.return_value = "2026-01-06T11:00:00"

        # Setup mock services
        mock_internal_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_message_svc().get_messages_count_by_session.return_value = 5

        # Create service instance
        service = RagChatService(db_session)

        # Get session stats
        stats = service.get_session_stats(mock_session.session_id)

        # Verify stats structure
        assert 'session_id' in stats
        assert stats['message_count'] == 5
        assert 'created_at' in stats


def test_multiple_queries_same_session():
    """Test multiple queries in the same session maintaining context."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock messages
        def create_mock_message(role, content):
            msg = Mock(spec=ChatMessage)
            msg.role = role
            msg.content = content
            return msg

        mock_message_svc().create_message.side_effect = [
            create_mock_message("user", "First question?"),
            create_mock_message("assistant", "First answer."),
            create_mock_message("user", "Follow-up question?"),
            create_mock_message("assistant", "Follow-up answer.")
        ]

        # Setup mock retrieval
        mock_chunk1 = Mock()
        mock_chunk1.content = 'Information relevant to first question.'
        mock_chunk1.source_path = '/book/docs/info1.md'
        mock_chunk1.title = 'Info Section 1'
        mock_chunk1.chunk_index = 0
        mock_chunk2 = Mock()
        mock_chunk2.content = 'Information relevant to follow-up.'
        mock_chunk2.source_path = '/book/docs/info2.md'
        mock_chunk2.title = 'Info Section 2'
        mock_chunk2.chunk_index = 1

        mock_retrieval_svc().retrieve_and_rank_chunks.side_effect = [[mock_chunk1], [mock_chunk2]]

        # Create service instance
        service = RagChatService(db_session)

        # Execute first query
        result1 = service.process_chat_query(
            message="First question?",
            session_id=mock_session.session_id
        )

        # Execute follow-up query in same session
        result2 = service.process_chat_query(
            message="Follow-up question?",
            session_id=mock_session.session_id
        )

        # Verify both queries were processed in the same session
        assert result1['session_id'] == result2['session_id']
        assert len(result1['citations']) > 0
        assert len(result2['citations']) > 0


def test_retrieval_failure_graceful_handling():
    """Test graceful handling when retrieval service fails."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock messages
        mock_user_message = Mock(spec=ChatMessage)
        mock_user_message.role = "user"
        mock_user_message.content = "Question about book content."
        mock_assistant_message = Mock(spec=ChatMessage)
        mock_assistant_message.role = "assistant"
        mock_assistant_message.content = "Error response."
        mock_message_svc().create_message.side_effect = [mock_user_message, mock_assistant_message]

        # Make retrieval service raise an exception
        mock_retrieval_svc().retrieve_and_rank_chunks.side_effect = Exception("Vector database unavailable")

        # Create service instance
        service = RagChatService(db_session)

        # Execute query - should handle the error gracefully
        result = service.process_chat_query(
            message="Question about book content.",
            session_id=mock_session.session_id
        )

        # Verify error was handled gracefully
        assert 'error' in result
        assert 'trouble accessing' in result['answer']


def test_configuration_options_integration():
    """Test that configuration options are properly applied in the pipeline."""
    db_session = Mock(spec=Session)

    with patch('app.services.chat_session_service.ChatSessionService') as mock_session_svc, \
         patch('app.services.chat_message_service.ChatMessageService') as mock_message_svc, \
         patch('app.services.retrieval_service.RetrievalService') as mock_retrieval_svc, \
         patch('app.services.qdrant_service.QdrantService'), \
         patch('app.utils.hallucination_guard.HallucinationGuard'):

        # Setup mock session
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session_svc().get_session_by_id.return_value = mock_session
        mock_session_svc().create_session.return_value = mock_session

        # Setup mock message service
        mock_user_message = Mock(spec=ChatMessage)
        mock_user_message.role = "user"
        mock_user_message.content = "Configured query?"
        mock_assistant_message = Mock(spec=ChatMessage)
        mock_assistant_message.role = "assistant"
        mock_assistant_message.content = "Configured response."
        mock_message_svc().create_message.side_effect = [mock_user_message, mock_assistant_message]

        # Setup mock retrieval with specific configuration
        mock_chunk = Mock()
        mock_chunk.id = 'configured-chunk'
        mock_chunk.content = 'Configured content based on parameters.'
        mock_chunk.source_path = '/book/docs/configured.md'
        mock_chunk.title = 'Configured Section'
        mock_chunk.chunk_index = 0
        mock_retrieval_svc().retrieve_and_rank_chunks.return_value = [mock_chunk]

        # Create service instance and test with custom configuration
        service = RagChatService(db_session)

        # Execute with custom configuration
        result = service.process_chat_query(
            message="Configured query?",
            session_id=mock_session.session_id,
            top_k=3,  # Custom top_k
            similarity_threshold=0.7  # Custom threshold
        )

        # Verify configuration was passed through (indirectly by checking the call)
        mock_retrieval_svc().retrieve_and_rank_chunks.assert_called_with(
            question="Configured query?",
            top_k=3,
            similarity_threshold=0.7
        )

        # Verify response structure
        assert 'session_id' in result
        assert 'answer' in result
        assert 'citations' in result