"""
Chat session service for the backend service.

This module provides CRUD operations for chat sessions,
including creation, retrieval, updating, and deletion.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from ..models.chat_session import ChatSession


class ChatSessionService:
    """
    Service class for handling chat session operations.

    Provides methods for creating, retrieving, updating, and deleting chat sessions
    with proper error handling and validation.
    """

    @staticmethod
    def create_session(db: Session, metadata: Optional[dict] = None) -> ChatSession:
        """
        Create a new chat session in the database.

        Args:
            db: Database session
            metadata: Optional metadata for the session

        Returns:
            ChatSession: Created chat session instance
        """
        session = ChatSession(session_metadata=metadata)
        db.add(session)
        try:
            db.commit()
            db.refresh(session)
            return session
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_session_by_id(db: Session, session_id: uuid.UUID) -> Optional[ChatSession]:
        """
        Retrieve a chat session by its ID.

        Args:
            db: Database session
            session_id: ID of the chat session to retrieve

        Returns:
            ChatSession: Chat session instance if found, None otherwise
        """
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    @staticmethod
    def get_all_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """
        Retrieve all chat sessions with pagination.

        Args:
            db: Database session
            skip: Number of sessions to skip (for pagination)
            limit: Maximum number of sessions to return

        Returns:
            List[ChatSession]: List of chat session instances
        """
        return db.query(ChatSession).offset(skip).limit(limit).all()

    @staticmethod
    def update_session(db: Session, session_id: uuid.UUID, **kwargs) -> Optional[ChatSession]:
        """
        Update a chat session's attributes.

        Args:
            db: Database session
            session_id: ID of the chat session to update
            **kwargs: Attributes to update

        Returns:
            ChatSession: Updated chat session instance if found, None otherwise
        """
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = __import__('datetime').datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session_id: uuid.UUID) -> bool:
        """
        Delete a chat session by its ID.

        Args:
            db: Database session
            session_id: ID of the chat session to delete

        Returns:
            bool: True if session was deleted, False if not found
        """
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def session_exists(db: Session, session_id: uuid.UUID) -> bool:
        """
        Check if a chat session with the given ID exists.

        Args:
            db: Database session
            session_id: ID to check

        Returns:
            bool: True if session exists, False otherwise
        """
        return db.query(ChatSession).filter(ChatSession.session_id == session_id).count() > 0