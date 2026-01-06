"""
API models for the RAG system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class RagQueryRequest(BaseModel):
    """
    Request model for RAG queries.
    """
    question: str = Field(
        ...,
        description="The question to answer using book content",
        example="What are the key concepts in Chapter 3?"
    )
    top_k: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Number of top results to retrieve (defaults to system setting)",
        example=5
    )
    similarity_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold (defaults to system setting)",
        example=0.5
    )
    include_citations: bool = Field(
        True,
        description="Whether to include citations in the response",
        example=True
    )


class RagQueryResponse(BaseModel):
    """
    Response model for RAG queries.
    """
    query_id: str = Field(
        ...,
        description="Unique identifier for the query",
        example="query-12345-abcde"
    )
    answer: str = Field(
        ...,
        description="The generated answer based on book content",
        example="The key concepts in Chapter 3 include..."
    )
    citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of citations for the information sources",
        example=[
            {
                "source_path": "/book/docs/chapter3.md",
                "heading": "Key Concepts",
                "chunk_index": 2,
                "preview": "The main concepts covered are..."
            }
        ]
    )
    retrieved_chunks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of chunks that were retrieved and used",
        example=[
            {
                "chunk_id": "chunk-123",
                "content": "The main concepts covered in this section...",
                "similarity_score": 0.85,
                "source_path": "/book/docs/chapter3.md"
            }
        ]
    )
    confidence_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for the response",
        example=0.85
    )
    processing_time_ms: float = Field(
        0.0,
        ge=0.0,
        description="Time taken to process the query in milliseconds",
        example=125.5
    )


class ChunkModel(BaseModel):
    """
    Model for document chunks.
    """
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    similarity_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentModel(BaseModel):
    """
    Model for documents.
    """
    document_id: str
    source_path: str
    title: str
    checksum: str
    created_at: datetime
    updated_at: datetime


class RetrievalStatsResponse(BaseModel):
    """
    Response model for retrieval statistics.
    """
    total_queries_processed: int
    average_response_time: float
    average_chunks_retrieved: int
    refusal_rate: float
    most_common_refusal_reasons: List[str]