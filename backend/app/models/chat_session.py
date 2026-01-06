"""
Chat session model for the backend service.

This module defines the SQLAlchemy model for chat sessions,
including fields for creation timestamp and session metadata.
"""
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseMixin
from ..database.connection import Base


class ChatSession(Base, BaseMixin):
    """
    SQLAlchemy model representing a chat session in the system.

    This model stores chat session information with timestamps
    for tracking when the session was created.
    """
    __tablename__ = "chat_sessions"

    def __repr__(self):
        """
        String representation of the ChatSession instance.

        Returns:
            str: String representation showing session ID and creation time
        """
        return f"<ChatSession(id={self.id}, created_at={self.created_at})>"

    def to_dict(self) -> dict:
        """
        Convert the ChatSession instance to a dictionary.

        Returns:
            dict: Dictionary representation of the chat session
        """
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }