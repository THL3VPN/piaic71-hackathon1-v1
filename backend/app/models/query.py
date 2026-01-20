"""
Query model for the RAG system.
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid


Base = declarative_base()


class Query(Base):
    """
    Represents a user query with metadata and relationship to retrieval results.
    """
    __tablename__ = "queries"

    query_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_question = Column(String, nullable=False)  # Original user question
    embedded_query = Column(Text, nullable=True)  # Vector representation as JSON string
    top_k = Column(Integer, default=5)  # Number of top results to retrieve
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Query(id={self.query_id}, question='{self.user_question[:50]}...')>"

    def to_dict(self):
        """Convert the query to a dictionary representation."""
        return {
            "query_id": str(self.query_id),
            "user_question": self.user_question,
            "embedded_query": self.embedded_query,
            "top_k": self.top_k,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }