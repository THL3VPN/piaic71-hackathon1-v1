"""
Chat message repository for the backend service.

This module provides data access operations for chat messages,
implementing the repository pattern for message-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.chat_message import ChatMessage


class ChatMessageRepository:
    """
    Repository class for chat message data access operations.

    Implements the repository pattern for chat message-related database operations,
    providing methods to interact with message data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create(self, session_id: uuid.UUID, role: str, content: str, citations: List[dict] = None) -> ChatMessage:
        """
        Create a new chat message.

        Args:
            session_id: ID of the session this message belongs to
            role: Role of the message sender (user/assistant)
            content: Content of the message
            citations: Optional citations for assistant messages

        Returns:
            ChatMessage: Created message instance
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_session(self, session_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """
        Retrieve messages for a specific session.

        Args:
            session_id: ID of the session to retrieve messages for
            limit: Maximum number of messages to return
            offset: Number of messages to skip (for pagination)

        Returns:
            List[ChatMessage]: List of messages in the session ordered by creation time
        """
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_by_id(self, message_id: uuid.UUID) -> Optional[ChatMessage]:
        """
        Retrieve a chat message by its ID.

        Args:
            message_id: ID of the message to retrieve

        Returns:
            ChatMessage: Message instance if found, None otherwise
        """
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def get_latest_for_session(self, session_id: uuid.UUID) -> Optional[ChatMessage]:
        """
        Get the most recent message for a session.

        Args:
            session_id: ID of the session to get latest message for

        Returns:
            ChatMessage: Most recent message in the session, None if no messages
        """
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

    def update(self, message_id: uuid.UUID, **kwargs) -> Optional[ChatMessage]:
        """
        Update a chat message's attributes.

        Args:
            message_id: ID of the message to update
            **kwargs: Attributes to update

        Returns:
            ChatMessage: Updated message instance if found, None otherwise
        """
        message = self.get_by_id(message_id)
        if message:
            for key, value in kwargs.items():
                setattr(message, key, value)
            self.db.commit()
            self.db.refresh(message)
        return message

    def delete(self, message_id: uuid.UUID) -> bool:
        """
        Delete a chat message by its ID.

        Args:
            message_id: ID of the message to delete

        Returns:
            bool: True if message was deleted, False if not found
        """
        message = self.get_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False