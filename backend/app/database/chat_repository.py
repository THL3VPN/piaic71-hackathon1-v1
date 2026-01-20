"""
Chat repository for the backend service.

This module provides data access operations for chat sessions and messages,
implementing the repository pattern for chat-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.chat_session import ChatSession
from ..models.chat_message import ChatMessage
from ..services.chat_session_service import ChatSessionService
from ..services.chat_message_service import ChatMessageService


class ChatRepository:
    """
    Repository class for chat data access operations.

    Implements the repository pattern for chat-related database operations,
    providing methods to interact with chat data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create_session(self) -> ChatSession:
        """
        Create a new chat session.

        Returns:
            ChatSession: Created chat session instance
        """
        return ChatSessionService.create_session(self.db)

    def get_session_by_id(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """
        Retrieve a chat session by its ID.

        Args:
            session_id: ID of the chat session to retrieve

        Returns:
            ChatSession: Chat session instance if found, None otherwise
        """
        return ChatSessionService.get_session_by_id(self.db, session_id)

    def get_all_sessions(self, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """
        Retrieve all chat sessions with pagination.

        Args:
            skip: Number of sessions to skip (for pagination)
            limit: Maximum number of sessions to return

        Returns:
            List[ChatSession]: List of chat session instances
        """
        return ChatSessionService.get_all_sessions(self.db, skip, limit)

    def update_session(self, session_id: uuid.UUID, **kwargs) -> Optional[ChatSession]:
        """
        Update a chat session's attributes.

        Args:
            session_id: ID of the chat session to update
            **kwargs: Attributes to update

        Returns:
            ChatSession: Updated chat session instance if found, None otherwise
        """
        return ChatSessionService.update_session(self.db, session_id, **kwargs)

    def delete_session(self, session_id: uuid.UUID) -> bool:
        """
        Delete a chat session by its ID.

        Args:
            session_id: ID of the chat session to delete

        Returns:
            bool: True if session was deleted, False if not found
        """
        return ChatSessionService.delete_session(self.db, session_id)

    def session_exists(self, session_id: uuid.UUID) -> bool:
        """
        Check if a chat session exists.

        Args:
            session_id: ID to check

        Returns:
            bool: True if session exists, False otherwise
        """
        return ChatSessionService.session_exists(self.db, session_id)

    def create_message(
        self,
        session_id: uuid.UUID,
        role: str,
        content: str
    ) -> ChatMessage:
        """
        Create a new chat message.

        Args:
            session_id: ID of the session this message belongs to
            role: Role of the message sender (user, assistant, system)
            content: Content of the message

        Returns:
            ChatMessage: Created chat message instance
        """
        return ChatMessageService.create_message(self.db, session_id, role, content)

    def get_message_by_id(self, message_id: uuid.UUID) -> Optional[ChatMessage]:
        """
        Retrieve a chat message by its ID.

        Args:
            message_id: ID of the chat message to retrieve

        Returns:
            ChatMessage: Chat message instance if found, None otherwise
        """
        return ChatMessageService.get_message_by_id(self.db, message_id)

    def get_messages_by_session_id(self, session_id: uuid.UUID) -> List[ChatMessage]:
        """
        Retrieve all messages for a specific session, ordered by creation time.

        Args:
            session_id: ID of the session to get messages for

        Returns:
            List[ChatMessage]: List of chat message instances ordered by creation time
        """
        return ChatMessageService.get_messages_by_session_id(self.db, session_id)

    def get_all_messages(self, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """
        Retrieve all chat messages with pagination.

        Args:
            skip: Number of messages to skip (for pagination)
            limit: Maximum number of messages to return

        Returns:
            List[ChatMessage]: List of chat message instances
        """
        return ChatMessageService.get_all_messages(self.db, skip, limit)

    def update_message(self, message_id: uuid.UUID, **kwargs) -> Optional[ChatMessage]:
        """
        Update a chat message's attributes.

        Args:
            message_id: ID of the chat message to update
            **kwargs: Attributes to update

        Returns:
            ChatMessage: Updated chat message instance if found, None otherwise
        """
        return ChatMessageService.update_message(self.db, message_id, **kwargs)

    def delete_message(self, message_id: uuid.UUID) -> bool:
        """
        Delete a chat message by its ID.

        Args:
            message_id: ID of the chat message to delete

        Returns:
            bool: True if message was deleted, False if not found
        """
        return ChatMessageService.delete_message(self.db, message_id)

    def message_exists(self, message_id: uuid.UUID) -> bool:
        """
        Check if a chat message exists.

        Args:
            message_id: ID to check

        Returns:
            bool: True if message exists, False otherwise
        """
        return ChatMessageService.message_exists(self.db, message_id)

    def get_messages_count_by_session(self, session_id: uuid.UUID) -> int:
        """
        Get the count of messages for a specific session.

        Args:
            session_id: ID of the session

        Returns:
            int: Number of messages for the session
        """
        return ChatMessageService.get_messages_count_by_session(self.db, session_id)

    def get_total_sessions_count(self) -> int:
        """
        Get the total count of chat sessions.

        Returns:
            int: Total number of chat sessions
        """
        return self.db.query(ChatSession).count()

    def get_total_messages_count(self) -> int:
        """
        Get the total count of chat messages.

        Returns:
            int: Total number of chat messages
        """
        return self.db.query(ChatMessage).count()