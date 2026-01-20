"""
Vector API Module

This module provides API endpoints for vector operations,
including upsert operations for document chunks and similarity search.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..config import settings
from ..services.qdrant_service import qdrant_service
from ..models.qdrant_models import QdrantUpsertRequest, QdrantUpsertResponse, QdrantSearchRequest, QdrantSearchResponse

router = APIRouter()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@router.post("/chunks/vector", response_model=QdrantUpsertResponse, summary="Upsert Chunk Vector")
async def upsert_chunk_vector(request: QdrantUpsertRequest) -> QdrantUpsertResponse:
    """
    Create or update a chunk's vector representation in Qdrant.

    Args:
        request: QdrantUpsertRequest containing chunk_id, vector, and metadata

    Returns:
        QdrantUpsertResponse indicating success and point ID

    Raises:
        HTTPException: If upsert operation fails
    """
    logger.info(f"Received upsert request for chunk ID: {request.chunk_id}")

    try:
        # Prepare payload with required metadata
        payload = {
            "document_id": request.document_id,
            "source_path": request.source_path,
            "title": request.title,
            "chunk_index": request.chunk_index
        }

        # Perform upsert operation
        success = qdrant_service.upsert_point(
            chunk_id=request.chunk_id,
            vector=request.vector,
            payload=payload
        )

        if success:
            logger.info(f"Successfully upserted vector for chunk ID: {request.chunk_id}")
            return QdrantUpsertResponse(success=True, point_id=request.chunk_id)
        else:
            logger.error(f"Failed to upsert vector for chunk ID: {request.chunk_id}")
            raise HTTPException(status_code=500, detail="Failed to upsert vector")

    except ValueError as ve:
        logger.error(f"Validation error during upsert: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error during upsert operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error during upsert: {str(e)}")


@router.post("/search/vector", response_model=QdrantSearchResponse, summary="Vector Similarity Search")
async def search_vector(request: QdrantSearchRequest) -> QdrantSearchResponse:
    """
    Search for similar chunks using vector similarity.

    Args:
        request: QdrantSearchRequest containing query vector and search parameters

    Returns:
        QdrantSearchResponse containing search results

    Raises:
        HTTPException: If search operation fails
    """
    logger.info(f"Received search request with limit: {request.limit}")

    try:
        # Perform similarity search
        results = qdrant_service.search_similar(
            query_vector=request.query_vector,
            limit=request.limit
        )

        logger.info(f"Search completed with {len(results)} results")
        return QdrantSearchResponse(results=results)

    except Exception as e:
        logger.error(f"Error during vector search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error during search: {str(e)}")