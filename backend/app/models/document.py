"""
Document model for the backend service.

This module defines the SQLAlchemy model for documents,
including fields for source path, title, checksum, content, and timestamps.
"""
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
import uuid

from .base import BaseMixin
from ..database.connection import Base
from sqlalchemy.orm import relationship


class Document(Base, BaseMixin):
    """
    SQLAlchemy model representing a source document with metadata and relationship to multiple chunks.

    This model stores document metadata including source path, title,
    checksum for change detection, full content, and timestamps for tracking.
    """
    __tablename__ = "documents"

    # Source path - must be unique across all documents
    source_path: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

    # Document title
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Checksum for change detection
    checksum: Mapped[str] = mapped_column(String(100), nullable=False)

    # Full document content after frontmatter removal
    content: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        """
        String representation of the Document instance.

        Returns:
            str: String representation showing document ID, path, and title
        """
        return f"<Document(id={self.id}, source_path='{self.source_path}', title='{self.title}')>"

    # Relationship to ingestion jobs
    ingestion_jobs = relationship("IngestionJob", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """
        Convert the Document instance to a dictionary.

        Returns:
            dict: Dictionary representation of the document
        """
        return {
            "id": str(self.id),
            "source_path": self.source_path,
            "title": self.title,
            "checksum": self.checksum,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }