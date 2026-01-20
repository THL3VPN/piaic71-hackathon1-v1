"""
Tests for chat session management functionality.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession
from app.services.chat_session_service import ChatSessionService


def test_create_session():
    """Test creating a new chat session."""
    from sqlalchemy.orm import Session
    import uuid

    with patch('sqlalchemy.orm.Session') as mock_db:
        # Create a real ChatSession instance with the new field name
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session.created_at = "2026-01-06T10:00:00"
        mock_session.session_metadata = {"user_id": "test-user"}

        # Configure the mock session to be returned after refresh
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'session_id', mock_session.session_id) or setattr(obj, 'created_at', mock_session.created_at) or setattr(obj, 'session_metadata', mock_session.session_metadata)

        # Mock the ChatSession constructor to return our mock session
        with patch('app.models.chat_session.ChatSession') as mock_model_class:
            mock_model_class.return_value = mock_session

            session = ChatSessionService.create_session(mock_db, metadata={"user_id": "test-user"})

            assert session is not None
            assert isinstance(session.session_id, uuid.UUID)
            mock_db.add.assert_called_once_with(mock_session)
            mock_db.commit.assert_called_once()


def test_get_session_by_id():
    """Test retrieving a chat session by its ID."""
    session_id = uuid.uuid4()

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = session_id
        mock_session.session_metadata = {"user_id": "test-user"}
        mock_repo.get_by_id.return_value = mock_session

        service = ChatSessionService(Session)
        retrieved_session = service.get_session_by_id(session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == session_id
        assert retrieved_session.session_metadata == {"user_id": "test-user"}
        mock_repo.get_by_id.assert_called_once_with(session_id)


def test_update_session():
    """Test updating a chat session's attributes."""
    session_id = uuid.uuid4()

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = session_id
        mock_session.session_metadata = {"user_id": "test-user"}
        mock_repo.update.return_value = mock_session

        service = ChatSessionService(Session)
        updated_session = service.update_session(session_id, metadata={"user_id": "updated-user", "context": "conversation"})

        assert updated_session is not None
        assert updated_session.session_id == session_id
        mock_repo.update.assert_called_once_with(session_id, metadata={"user_id": "updated-user", "context": "conversation"})


def test_delete_session():
    """Test deleting a chat session by its ID."""
    session_id = uuid.uuid4()

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_repo.delete.return_value = True

        service = ChatSessionService(Session)
        result = service.delete_session(session_id)

        assert result is True
        mock_repo.delete.assert_called_once_with(session_id)


def test_session_exists():
    """Test checking if a chat session exists."""
    session_id = uuid.uuid4()

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_repo.get_by_id.return_value = Mock(spec=ChatSession)  # Session exists

        service = ChatSessionService(Session)
        exists = service.session_exists(session_id)

        assert exists is True
        mock_repo.get_by_id.assert_called_once_with(session_id)


def test_session_not_exists():
    """Test checking if a non-existent chat session exists."""
    session_id = uuid.uuid4()

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_repo.get_by_id.return_value = None  # Session doesn't exist

        service = ChatSessionService(Session)
        exists = service.session_exists(session_id)

        assert exists is False
        mock_repo.get_by_id.assert_called_once_with(session_id)


def test_validate_session_exists():
    """Test the validate_session_exists method."""
    session_id = uuid.uuid4()

    with patch.object(ChatSessionService, 'get_session_by_id') as mock_get:
        mock_get.return_value = Mock(spec=ChatSession)  # Session exists

        service = ChatSessionService(Session)
        result = service.validate_session_exists(session_id)

        assert result is True


def test_validate_session_not_exists():
    """Test the validate_session_exists method with non-existent session."""
    session_id = uuid.uuid4()

    with patch.object(ChatSessionService, 'get_session_by_id') as mock_get:
        mock_get.return_value = None  # Session doesn't exist

        service = ChatSessionService(Session)
        result = service.validate_session_exists(session_id)

        assert result is False


def test_ensure_session_exists_existing():
    """Test ensure_session_exists with existing session."""
    session_id = uuid.uuid4()

    with patch.object(ChatSessionService, 'get_session') as mock_get, \
         patch.object(ChatSessionService, 'create_session') as mock_create:

        mock_session = Mock(spec=ChatSession)
        mock_get.return_value = mock_session  # Session exists
        mock_create.return_value = None  # Won't be called

        service = ChatSessionService(Session)
        result = service.ensure_session_exists(session_id)

        assert result == mock_session
        mock_get.assert_called_once_with(session_id)
        mock_create.assert_not_called()


def test_ensure_session_exists_new():
    """Test ensure_session_exists with non-existing session."""
    session_id = uuid.uuid4()

    with patch.object(ChatSessionService, 'get_session') as mock_get, \
         patch.object(ChatSessionService, 'create_session') as mock_create:

        mock_get.return_value = None  # Session doesn't exist
        mock_new_session = Mock(spec=ChatSession)
        mock_create.return_value = mock_new_session

        service = ChatSessionService(Session)
        result = service.ensure_session_exists(session_id)

        assert result == mock_new_session
        mock_get.assert_called_once_with(session_id)
        mock_create.assert_called_once()


def test_session_creation_without_metadata():
    """Test creating a session without providing metadata."""
    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_session = Mock(spec=ChatSession)
        mock_session.session_id = uuid.uuid4()
        mock_session.session_metadata = None
        mock_repo.create.return_value = mock_session

        service = ChatSessionService(Session)
        session = service.create_session()

        assert session is not None
        assert isinstance(session.session_id, uuid.UUID)
        assert session.session_metadata is None
        mock_repo.create.assert_called_once_with(metadata=None)


def test_session_lifespan_management():
    """Test session lifespan and cleanup functionality."""
    # This would test session timeout and cleanup mechanisms
    # For now, verify that sessions can be properly managed
    session_ids = [uuid.uuid4() for _ in range(3)]

    with patch('app.database.chat_session_repository.ChatSessionRepository') as mock_repo:
        mock_repo.get_by_id.side_effect = lambda sid: Mock(spec=ChatSession, session_id=sid) if sid in session_ids[:2] else None

        service = ChatSessionService(Session)

        # Check that existing sessions are found
        for sid in session_ids[:2]:
            assert service.session_exists(sid) is True

        # Check that non-existing session is not found
        assert service.session_exists(session_ids[2]) is False