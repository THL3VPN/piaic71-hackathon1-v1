"""
Citation model for the RAG system.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid


Base = declarative_base()


class Citation(Base):
    """
    Represents a citation for a retrieved chunk with source information.
    """
    __tablename__ = "citations"

    citation_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bundle_id = Column(PG_UUID(as_uuid=True), ForeignKey("context_bundles.bundle_id"), nullable=False)
    chunk_id = Column(PG_UUID(as_uuid=True), ForeignKey("chunks.id"), nullable=False)  # Assuming chunk IDs are UUIDs
    source_path = Column(String(500), nullable=False)  # Path to the source document
    heading = Column(String(200), nullable=True)  # Heading where chunk appears
    chunk_index = Column(Integer, nullable=False)  # Index of chunk in document
    citation_text = Column(Text, nullable=True)  # Formatted citation string
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bundle = relationship("ContextBundle", back_populates="citations")
    chunk = relationship("Chunk", back_populates="citations")  # Assuming Chunk model exists

    def __repr__(self):
        return f"<Citation(id={self.citation_id}, source_path='{self.source_path}', chunk_index={self.chunk_index})>"

    def to_dict(self):
        """Convert the citation to a dictionary representation."""
        return {
            "citation_id": str(self.citation_id),
            "bundle_id": str(self.bundle_id),
            "chunk_id": str(self.chunk_id),
            "source_path": self.source_path,
            "heading": self.heading,
            "chunk_index": self.chunk_index,
            "citation_text": self.citation_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }