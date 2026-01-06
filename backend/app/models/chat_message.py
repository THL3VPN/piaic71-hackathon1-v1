"""
Chat message model for the backend service.

This module defines the SQLAlchemy model for chat messages,
including fields for session reference, role, content, and timestamps.
"""
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseMixin
from ..database.connection import Base
from .chat_session import ChatSession


class ChatMessage(Base, BaseMixin):
    """
    SQLAlchemy model representing a chat message in the system.

    This model stores chat message information including the session it belongs to,
    the role (user, assistant, system), the content of the message, and timestamps.
    """
    __tablename__ = "chat_messages"

    # Session reference - foreign key to chat_sessions table
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Role of the message sender (user, assistant, system)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # Content of the message
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self):
        """
        String representation of the ChatMessage instance.

        Returns:
            str: String representation showing message ID, session ID, and role
        """
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role={self.role})>"

    def to_dict(self) -> dict:
        """
        Convert the ChatMessage instance to a dictionary.

        Returns:
            dict: Dictionary representation of the chat message
        """
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }