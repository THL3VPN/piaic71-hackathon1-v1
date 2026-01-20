"""
Ingestion job model for the backend service.

This module defines the IngestionJob SQLAlchemy model for tracking document ingestion jobs,
including their status, progress, and metadata.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from typing import Optional
import uuid
from datetime import datetime
from ..database.connection import Base


class IngestionJob(Base):
    """
    SQLAlchemy model for tracking document ingestion jobs.

    This model represents a document ingestion job with status tracking,
    progress information, and metadata about the ingestion process.
    """
    __tablename__ = "ingestion_jobs"

    # Primary key with UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key reference to document being ingested
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)

    # Document relationship
    document = relationship("Document", back_populates="ingestion_jobs")

    # Status of the ingestion job (pending, processing, completed, failed)
    status = Column(String(50), nullable=False, default="pending", index=True)

    # Progress percentage (0-100)
    progress = Column(Integer, nullable=False, default=0)

    # Total number of chunks to process
    total_chunks = Column(Integer, nullable=True)

    # Number of chunks processed
    processed_chunks = Column(Integer, nullable=False, default=0)

    # Error message if job failed
    error_message = Column(Text, nullable=True)

    # Additional metadata about the ingestion job (using JSONB for PostgreSQL, Text for SQLite compatibility)
    # For production PostgreSQL, this will be JSONB; for testing with SQLite, this is Text
    job_metadata = Column(Text, nullable=True)  # Will store JSON string for SQLite compatibility

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<IngestionJob(id={self.id}, document_id={self.document_id}, status='{self.status}')>"

    @property
    def parsed_job_metadata(self):
        """
        Get the deserialized job metadata from the JSON string.

        Returns:
            dict or None: Deserialized job metadata or None if not available
        """
        import json
        if self.job_metadata:
            try:
                return json.loads(self.job_metadata)
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, return as-is
                return self.job_metadata
        return None

    def to_dict(self):
        """
        Convert the IngestionJob instance to a dictionary representation.

        Returns:
            dict: Dictionary representation of the IngestionJob
        """
        import json

        # Deserialize job_metadata from JSON string if it exists
        job_metadata = None
        if self.job_metadata:
            try:
                job_metadata = json.loads(self.job_metadata)
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, return as-is
                job_metadata = self.job_metadata

        return {
            "id": str(self.id),
            "document_id": str(self.document_id),
            "status": self.status,
            "progress": self.progress,
            "total_chunks": self.total_chunks,
            "processed_chunks": self.processed_chunks,
            "error_message": self.error_message,
            "job_metadata": job_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }