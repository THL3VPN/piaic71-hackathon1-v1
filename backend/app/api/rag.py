"""
RAG API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.database.connection import get_db
from app.services.rag_service import RagService
from app.api.models import RagQueryRequest, RagQueryResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/query", response_model=RagQueryResponse)
async def query_documents(
    request: RagQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query the RAG system with a question about book content.

    Args:
        request: Query request with question and optional parameters
        db: Database session

    Returns:
        Query response with answer and citations
    """
    logger.info(f"Received RAG query: {request.question[:50]}...")

    try:
        # Initialize RAG service with database session
        rag_service = RagService(db)

        # Process the query
        result = rag_service.process_query(
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )

        # Log the result
        if result.get("was_refused"):
            logger.info(f"Query refused: {result.get('refusal_reason')}")
        else:
            logger.info(f"Query processed successfully with {len(result.get('citations', []))} citations")

        # Return the response
        return RagQueryResponse(
            query_id="temp-id",  # In a real implementation, this would be a proper UUID
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
            retrieved_chunks=result.get("retrieved_chunks", []),
            confidence_score=result.get("confidence_score", 0.0),
            processing_time_ms=0.0  # In a real implementation, measure actual processing time
        )

    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/health")
async def rag_health():
    """
    Health check for the RAG service.

    Returns:
        Health status
    """
    return {"status": "healthy", "component": "rag-service"}


@router.get("/stats")
async def get_retrieval_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about the RAG retrieval system.

    Args:
        db: Database session

    Returns:
        Retrieval statistics
    """
    try:
        rag_service = RagService(db)
        stats = rag_service.get_retrieval_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting retrieval stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")