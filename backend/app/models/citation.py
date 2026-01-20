"""
Citation model for the backend service.

This module defines the SQLAlchemy model for citations that link
to specific parts of documents, including source path, title, and chunk index.
"""
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from typing import Optional

from .base import BaseMixin
from ..database.connection import Base


class Citation(Base, BaseMixin):
    """
    SQLAlchemy model representing a citation in the system.

    This model stores citation information that links to specific parts of documents,
    including source path, title, chunk index, and snippet for reference purposes.
    """
    __tablename__ = "citations"

    # Message reference - foreign key to chat_messages table
    message_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False
    )

    # Path to the source document
    source_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Title of the document section
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Index of the chunk in the document
    chunk_index: Mapped[int] = mapped_column(nullable=False)

    # Short text snippet from the source
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        """
        String representation of the Citation instance.

        Returns:
            str: String representation showing citation ID, source path, and chunk index
        """
        return f"<Citation(id={self.id}, source_path={self.source_path}, chunk_index={self.chunk_index})>"

    def to_dict(self) -> dict:
        """
        Convert the Citation instance to a dictionary.

        Returns:
            dict: Dictionary representation of the citation
        """
        return {
            "id": str(self.id),
            "message_id": str(self.message_id),
            "source_path": self.source_path,
            "title": self.title,
            "chunk_index": self.chunk_index,
            "snippet": self.snippet,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }