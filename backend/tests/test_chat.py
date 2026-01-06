"""
Chat operations tests for the backend service.

This module contains tests for chat session and message operations,
verifying that chat sessions can be created, retrieved, updated, and deleted properly,
and that messages can be added to and retrieved from sessions.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import uuid

from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.database.chat_repository import ChatRepository
from app.database.connection import Base


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    # Ensure all models are registered with Base metadata before creating tables
    # Models are imported at the top of the file
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def test_chat_session_creation(db_session):
    """Test that chat sessions can be created successfully."""
    session = ChatSessionService.create_session(db_session)

    assert session is not None
    assert session.id is not None
    assert session.created_at is not None


def test_chat_session_retrieval_by_id(db_session):
    """Test that chat sessions can be retrieved by ID."""
    created_session = ChatSessionService.create_session(db_session)

    retrieved_session = ChatSessionService.get_session_by_id(db_session, created_session.id)

    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id
    assert retrieved_session.created_at == created_session.created_at


def test_chat_session_does_not_exist(db_session):
    """Test that retrieving a non-existent chat session returns None."""
    non_existent_id = uuid.uuid4()
    retrieved_session = ChatSessionService.get_session_by_id(db_session, non_existent_id)
    assert retrieved_session is None


def test_chat_session_update(db_session):
    """Test that chat sessions can be updated."""
    session = ChatSessionService.create_session(db_session)

    # Note: ChatSession doesn't have updateable fields other than timestamps
    # The service method exists for consistency but won't change the session
    updated_session = ChatSessionService.update_session(db_session, session.id)
    assert updated_session is not None
    assert updated_session.id == session.id


def test_chat_session_deletion(db_session):
    """Test that chat sessions can be deleted."""
    session = ChatSessionService.create_session(db_session)

    # Verify session exists
    retrieved_session = ChatSessionService.get_session_by_id(db_session, session.id)
    assert retrieved_session is not None

    # Delete the session
    deleted = ChatSessionService.delete_session(db_session, session.id)
    assert deleted is True

    # Verify session no longer exists
    retrieved_session = ChatSessionService.get_session_by_id(db_session, session.id)
    assert retrieved_session is None


def test_chat_session_exists(db_session):
    """Test that chat session existence check works."""
    session = ChatSessionService.create_session(db_session)

    # Session should exist
    exists = ChatSessionService.session_exists(db_session, session.id)
    assert exists is True

    # Non-existent session should not exist
    exists = ChatSessionService.session_exists(db_session, uuid.uuid4())
    assert exists is False


def test_chat_message_creation(db_session):
    """Test that chat messages can be created successfully."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    message = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="Hello, this is a test message."
    )

    assert message is not None
    assert message.session_id == chat_session.id
    assert message.role == "user"
    assert message.content == "Hello, this is a test message."
    assert message.created_at is not None


def test_chat_message_retrieval_by_id(db_session):
    """Test that chat messages can be retrieved by ID."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    created_message = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="assistant",
        content="Hello! How can I help you?"
    )

    retrieved_message = ChatMessageService.get_message_by_id(db_session, created_message.id)

    assert retrieved_message is not None
    assert retrieved_message.id == created_message.id
    assert retrieved_message.session_id == chat_session.id
    assert retrieved_message.role == "assistant"
    assert retrieved_message.content == "Hello! How can I help you?"


def test_chat_message_retrieval_by_session(db_session):
    """Test that all messages for a session can be retrieved."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    # Create multiple messages for the same session
    msg1 = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="First message"
    )
    msg2 = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="assistant",
        content="Second message"
    )
    msg3 = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="Third message"
    )

    messages = ChatMessageService.get_messages_by_session_id(db_session, chat_session.id)

    assert len(messages) == 3
    # Check that they are ordered by creation time (first message first)
    assert messages[0].id == msg1.id
    assert messages[1].id == msg2.id
    assert messages[2].id == msg3.id
    assert messages[0].content == "First message"
    assert messages[1].content == "Second message"
    assert messages[2].content == "Third message"


def test_chat_message_does_not_exist(db_session):
    """Test that retrieving a non-existent chat message returns None."""
    non_existent_id = uuid.uuid4()
    retrieved_message = ChatMessageService.get_message_by_id(db_session, non_existent_id)
    assert retrieved_message is None


def test_chat_message_update(db_session):
    """Test that chat messages can be updated."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    message = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="Original message content."
    )

    updated_message = ChatMessageService.update_message(
        db_session, message.id, content="Updated message content."
    )

    assert updated_message is not None
    assert updated_message.content == "Updated message content."


def test_chat_message_deletion(db_session):
    """Test that chat messages can be deleted."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    message = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="Message to be deleted."
    )

    # Verify message exists
    retrieved_message = ChatMessageService.get_message_by_id(db_session, message.id)
    assert retrieved_message is not None

    # Delete the message
    deleted = ChatMessageService.delete_message(db_session, message.id)
    assert deleted is True

    # Verify message no longer exists
    retrieved_message = ChatMessageService.get_message_by_id(db_session, message.id)
    assert retrieved_message is None


def test_chat_message_exists(db_session):
    """Test that chat message existence check works."""
    # Create a session first
    chat_session = ChatSessionService.create_session(db_session)

    message = ChatMessageService.create_message(
        db_session,
        session_id=chat_session.id,
        role="user",
        content="Test message for existence check."
    )

    # Message should exist
    exists = ChatMessageService.message_exists(db_session, message.id)
    assert exists is True

    # Non-existent message should not exist
    exists = ChatMessageService.message_exists(db_session, uuid.uuid4())
    assert exists is False


def test_chat_repository_pattern(db_session):
    """Test that the chat repository pattern works correctly."""
    # Create repository instance
    repo = ChatRepository(db_session)

    # Create session via repository
    created_session = repo.create_session()
    assert created_session is not None
    assert created_session.id is not None

    # Retrieve session via repository
    retrieved_session = repo.get_session_by_id(created_session.id)
    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id

    # Create message via repository
    created_message = repo.create_message(
        session_id=created_session.id,
        role="user",
        content="Repository test message."
    )
    assert created_message is not None
    assert created_message.session_id == created_session.id

    # Retrieve message via repository
    retrieved_message = repo.get_message_by_id(created_message.id)
    assert retrieved_message is not None
    assert retrieved_message.id == created_message.id

    # Retrieve messages by session via repository
    messages_by_session = repo.get_messages_by_session_id(created_session.id)
    assert len(messages_by_session) == 1
    assert messages_by_session[0].id == created_message.id

    # Check if session exists via repository
    exists = repo.session_exists(created_session.id)
    assert exists is True

    # Check if message exists via repository
    exists = repo.message_exists(created_message.id)
    assert exists is True

    # Get all messages for session via repository
    all_messages = repo.get_messages_by_session_id(created_session.id)
    assert len(all_messages) == 1

    # Update message via repository
    updated_message = repo.update_message(created_message.id, content="Updated via Repo")
    assert updated_message is not None
    assert updated_message.content == "Updated via Repo"

    # Get message count by session via repository
    count = repo.get_messages_count_by_session(created_session.id)
    assert count == 1

    # Delete message via repository
    deleted = repo.delete_message(created_message.id)
    assert deleted is True

    # Verify deletion
    retrieved_message = repo.get_message_by_id(created_message.id)
    assert retrieved_message is None

    # Delete session via repository
    deleted = repo.delete_session(created_session.id)
    assert deleted is True

    # Verify session deletion
    retrieved_session = repo.get_session_by_id(created_session.id)
    assert retrieved_session is None