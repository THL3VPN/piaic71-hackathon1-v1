"""
Chat message service for the backend service.

This module provides CRUD operations for chat messages,
including creation, retrieval, updating, and deletion.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from ..models.chat_message import ChatMessage


class ChatMessageService:
    """
    Service class for handling chat message operations.

    Provides methods for creating, retrieving, updating, and deleting chat messages
    with proper error handling and validation.
    """

    @staticmethod
    def create_message(
        db: Session,
        session_id: uuid.UUID,
        role: str,
        content: str
    ) -> ChatMessage:
        """
        Create a new chat message in the database.

        Args:
            db: Database session
            session_id: ID of the session this message belongs to
            role: Role of the message sender (user, assistant, system)
            content: Content of the message

        Returns:
            ChatMessage: Created chat message instance
        """
        # Validate role
        valid_roles = ["user", "assistant", "system"]
        if role not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")

        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(message)
        try:
            db.commit()
            db.refresh(message)
            return message
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_message_by_id(db: Session, message_id: uuid.UUID) -> Optional[ChatMessage]:
        """
        Retrieve a chat message by its ID.

        Args:
            db: Database session
            message_id: ID of the chat message to retrieve

        Returns:
            ChatMessage: Chat message instance if found, None otherwise
        """
        return db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    @staticmethod
    def get_messages_by_session_id(db: Session, session_id: uuid.UUID) -> List[ChatMessage]:
        """
        Retrieve all messages for a specific session, ordered by creation time.

        Args:
            db: Database session
            session_id: ID of the session to get messages for

        Returns:
            List[ChatMessage]: List of chat message instances ordered by creation time
        """
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()

    @staticmethod
    def get_all_messages(db: Session, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """
        Retrieve all chat messages with pagination.

        Args:
            db: Database session
            skip: Number of messages to skip (for pagination)
            limit: Maximum number of messages to return

        Returns:
            List[ChatMessage]: List of chat message instances
        """
        return db.query(ChatMessage).offset(skip).limit(limit).all()

    @staticmethod
    def update_message(db: Session, message_id: uuid.UUID, **kwargs) -> Optional[ChatMessage]:
        """
        Update a chat message's attributes.

        Args:
            db: Database session
            message_id: ID of the chat message to update
            **kwargs: Attributes to update

        Returns:
            ChatMessage: Updated chat message instance if found, None otherwise
        """
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            for key, value in kwargs.items():
                if hasattr(message, key):
                    setattr(message, key, value)
            message.updated_at = __import__('datetime').datetime.utcnow()
            db.commit()
            db.refresh(message)
        return message

    @staticmethod
    def delete_message(db: Session, message_id: uuid.UUID) -> bool:
        """
        Delete a chat message by its ID.

        Args:
            db: Database session
            message_id: ID of the chat message to delete

        Returns:
            bool: True if message was deleted, False if not found
        """
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False

    @staticmethod
    def message_exists(db: Session, message_id: uuid.UUID) -> bool:
        """
        Check if a chat message with the given ID exists.

        Args:
            db: Database session
            message_id: ID to check

        Returns:
            bool: True if message exists, False otherwise
        """
        return db.query(ChatMessage).filter(ChatMessage.id == message_id).count() > 0

    @staticmethod
    def get_messages_count_by_session(db: Session, session_id: uuid.UUID) -> int:
        """
        Get the count of messages for a specific session.

        Args:
            db: Database session
            session_id: ID of the session

        Returns:
            int: Number of messages for the session
        """
        return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()