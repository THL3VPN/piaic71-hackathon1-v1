"""
Pydantic models for Qdrant vector operations.

This module defines Pydantic models for Qdrant vector operations,
including request and response models for upsert and search operations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class QdrantUpsertRequest(BaseModel):
    """
    Request model for upserting vector data to Qdrant.
    """
    chunk_id: str = Field(
        ...,
        description="UUID of the chunk (used as Qdrant point ID)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    vector: List[float] = Field(
        ...,
        description="Embedding vector",
        example=[0.1, 0.2, 0.3, 0.4, 0.5]
    )
    document_id: str = Field(
        ...,
        description="Document UUID for payload",
        example="550e8400-e29b-41d4-a716-446655440001"
    )
    source_path: str = Field(
        ...,
        description="Document source path",
        example="path/to/document.pdf"
    )
    title: str = Field(
        ...,
        description="Document title",
        example="Sample Document Title"
    )
    chunk_index: int = Field(
        ...,
        description="Chunk sequence number",
        example=0,
        ge=0
    )


class QdrantUpsertResponse(BaseModel):
    """
    Response model for Qdrant upsert operations.
    """
    success: bool = Field(..., description="Whether the upsert was successful")
    point_id: str = Field(..., description="ID of the upserted point")


class QdrantSearchRequest(BaseModel):
    """
    Request model for vector similarity search in Qdrant.
    """
    query_vector: List[float] = Field(
        ...,
        description="Query embedding vector",
        example=[0.1, 0.2, 0.3, 0.4, 0.5]
    )
    limit: int = Field(
        10,
        description="Maximum number of results to return",
        ge=1,
        le=100
    )
    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional filters for search"
    )


class QdrantSearchResult(BaseModel):
    """
    Model for individual search result from Qdrant.
    """
    chunk_id: str = Field(..., description="ID of the matching chunk")
    document_id: str = Field(..., description="ID of the document")
    source_path: str = Field(..., description="Source path of the document")
    title: str = Field(..., description="Title of the document")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    score: float = Field(..., description="Similarity score")


class QdrantSearchResponse(BaseModel):
    """
    Response model for Qdrant vector search operations.
    """
    results: List[QdrantSearchResult] = Field(..., description="List of search results")


class QdrantHealthResponse(BaseModel):
    """
    Response model for Qdrant health check.
    """
    status: str = Field(..., description="Health status", example="healthy")
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional health details"
    )


class QdrantCollectionCheck(BaseModel):
    """
    Model for Qdrant collection health details.
    """
    qdrant_connected: bool = Field(..., description="Whether Qdrant is connected")
    collection_exists: bool = Field(..., description="Whether the collection exists")
    collection_name: str = Field(..., description="Name of the collection")