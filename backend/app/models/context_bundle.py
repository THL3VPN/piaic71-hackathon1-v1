"""
Context bundle model for the RAG system.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid


Base = declarative_base()


class ContextBundle(Base):
    """
    Represents a collection of relevant chunks and citations used to answer a user's question.
    """
    __tablename__ = "context_bundles"

    bundle_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(PG_UUID(as_uuid=True), ForeignKey("queries.query_id"), nullable=False)
    retrieved_chunks = Column(Text, nullable=False)  # JSON string of retrieved chunks
    formatted_context = Column(Text, nullable=True)  # Formatted context with citations
    token_count = Column(Integer, nullable=True)  # Number of tokens in the context
    created_at = Column(DateTime, default=datetime.utcnow)


    def __repr__(self):
        return f"<ContextBundle(id={self.bundle_id}, query_id={self.query_id})>"

    def to_dict(self):
        """Convert the context bundle to a dictionary representation."""
        return {
            "bundle_id": str(self.bundle_id),
            "query_id": str(self.query_id),
            "retrieved_chunks": self.retrieved_chunks,
            "formatted_context": self.formatted_context,
            "token_count": self.token_count,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }