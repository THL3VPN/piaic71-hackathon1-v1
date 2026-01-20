"""
Chat session repository for the backend service.

This module provides data access operations for chat sessions,
implementing the repository pattern for session-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.chat_session import ChatSession


class ChatSessionRepository:
    """
    Repository class for chat session data access operations.

    Implements the repository pattern for chat session-related database operations,
    providing methods to interact with session data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create(self, metadata: dict = None) -> ChatSession:
        """
        Create a new chat session.

        Args:
            metadata: Optional session metadata

        Returns:
            ChatSession: Created session instance
        """
        session = ChatSession(metadata=metadata)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """
        Retrieve a chat session by its ID.

        Args:
            session_id: ID of the session to retrieve

        Returns:
            ChatSession: Session instance if found, None otherwise
        """
        return self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()

    def update(self, session_id: uuid.UUID, **kwargs) -> Optional[ChatSession]:
        """
        Update a chat session's attributes.

        Args:
            session_id: ID of the session to update
            **kwargs: Attributes to update

        Returns:
            ChatSession: Updated session instance if found, None otherwise
        """
        session = self.get_by_id(session_id)
        if session:
            for key, value in kwargs.items():
                setattr(session, key, value)
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete(self, session_id: uuid.UUID) -> bool:
        """
        Delete a chat session by its ID.

        Args:
            session_id: ID of the session to delete

        Returns:
            bool: True if session was deleted, False if not found
        """
        session = self.get_by_id(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False