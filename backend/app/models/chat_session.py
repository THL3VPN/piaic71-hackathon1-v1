"""
Chat session model for the backend service.

This module defines the SQLAlchemy model for chat sessions,
including fields for session ID, timestamps, and metadata.
"""
from sqlalchemy import DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from typing import Optional, Dict, Any

from .base import BaseMixin
from ..database.connection import Base


class ChatSession(Base, BaseMixin):
    """
    SQLAlchemy model representing a chat session in the system.

    This model stores chat session information including session ID,
    creation/update timestamps, and optional metadata for session management.
    """
    __tablename__ = "chat_sessions"

    # Session identifier - primary key using UUID
    session_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Optional metadata for the session (e.g., user preferences, conversation context)
    session_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        """
        String representation of the ChatSession instance.

        Returns:
            str: String representation showing session ID and creation timestamp
        """
        return f"<ChatSession(session_id={self.session_id}, created_at={self.created_at})>"

    def to_dict(self) -> dict:
        """
        Convert the ChatSession instance to a dictionary.

        Returns:
            dict: Dictionary representation of the chat session
        """
        return {
            "session_id": str(self.session_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.session_metadata
        }