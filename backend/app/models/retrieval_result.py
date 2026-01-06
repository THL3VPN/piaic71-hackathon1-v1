"""
Retrieval result model for the RAG system.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import uuid


Base = declarative_base()


class RetrievalResult(Base):
    """
    Represents the results of a retrieval operation with chunk IDs and metadata.
    """
    __tablename__ = "retrieval_results"

    result_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(PG_UUID(as_uuid=True), ForeignKey("queries.query_id"), nullable=False)
    chunk_ids = Column(Text, nullable=False)  # JSON string of chunk IDs
    confidence_scores = Column(Text, nullable=True)  # JSON string of confidence scores
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    retrieval_time_ms = Column(Integer, nullable=True)  # Time taken for retrieval in milliseconds


    def __repr__(self):
        return f"<RetrievalResult(id={self.result_id}, query_id={self.query_id})>"

    def to_dict(self):
        """Convert the retrieval result to a dictionary representation."""
        return {
            "result_id": str(self.result_id),
            "query_id": str(self.query_id),
            "chunk_ids": self.chunk_ids,
            "confidence_scores": self.confidence_scores,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
            "retrieval_time_ms": self.retrieval_time_ms
        }