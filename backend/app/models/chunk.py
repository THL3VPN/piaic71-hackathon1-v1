"""
Chunk model for the backend service.

This module defines the SQLAlchemy model for document chunks,
including fields for document reference, index, content, hash, vector, metadata, and timestamps.
"""
from sqlalchemy import String, Integer, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseMixin
from ..database.connection import Base
from .document import Document


class Chunk(Base, BaseMixin):
    """
    SQLAlchemy model representing a document chunk in the system.

    This model stores document content chunks with their metadata,
    including document reference, index, content, hash for deduplication,
    vector embedding for similarity search, and JSONB metadata for flexible storage.
    """
    __tablename__ = "chunks"

    # Document reference - foreign key to documents table
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    # Sequential index of the chunk within the document
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # The actual content of the chunk
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Stable hash for deduplication
    chunk_hash: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Vector embedding stored as JSON
    vector: Mapped[dict] = mapped_column(Text, nullable=True)

    # Flexible metadata (headings, anchors, etc.) - stored as JSON text
    chunk_metadata: Mapped[dict] = mapped_column(Text, nullable=True)

    def __repr__(self):
        """
        String representation of the Chunk instance.

        Returns:
            str: String representation showing chunk ID, document ID, and index
        """
        return f"<Chunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"

    def to_dict(self) -> dict:
        """
        Convert the Chunk instance to a dictionary.

        Returns:
            dict: Dictionary representation of the chunk
        """
        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "chunk_index": self.chunk_index,
            "chunk_text": self.chunk_text,
            "chunk_hash": self.chunk_hash,
            "vector": self.vector,
            "metadata": self.chunk_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }