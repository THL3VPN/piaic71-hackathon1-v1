"""
Chat API endpoints for the RAG chatbot.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import logging

from app.database.connection import get_db
from app.services.rag_chat_service import RagChatService
from app.api.models import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint for the RAG chatbot.

    Args:
        request: Chat request with message and optional session ID
        db: Database session

    Returns:
        Chat response with answer and citations
    """
    logger.info(f"Received chat message: {request.message[:50]}...")

    try:
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Initialize RAG chat service with database session
        rag_chat_service = RagChatService(db)

        # Process the chat query
        result = rag_chat_service.process_chat_query(
            message=request.message,
            session_id=uuid.UUID(request.session_id) if request.session_id else None,
            top_k=request.top_k if request.top_k else 5,
            similarity_threshold=request.similarity_threshold if request.similarity_threshold else 0.5
        )

        logger.info(f"Chat processed successfully with {len(result.get('citations', []))} citations")

        # Return the response
        return ChatResponse(
            session_id=result["session_id"],
            answer=result["answer"],
            citations=result.get("citations", []),
            retrieved_chunks_count=result.get("retrieved_chunks_count", 0)
        )

    except ValueError as ve:
        # Handle UUID parsing errors
        logger.error(f"Value error processing chat: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get information about a specific chat session.

    Args:
        session_id: ID of the session to retrieve
        db: Database session

    Returns:
        Session information
    """
    try:
        rag_chat_service = RagChatService(db)

        # Validate session exists
        if not rag_chat_service.validate_chat_session(uuid.UUID(session_id)):
            raise HTTPException(status_code=404, detail="Session not found")

        # Get session stats
        stats = rag_chat_service.get_session_stats(uuid.UUID(session_id))

        return {
            "session_id": session_id,
            "exists": True,
            "stats": stats
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.get("/sessions/{session_id}/history")
async def get_conversation_history(
    session_id: str,
    limit: Optional[int] = 50,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a specific session.

    Args:
        session_id: ID of the session to retrieve history for
        limit: Maximum number of messages to return
        db: Database session

    Returns:
        List of conversation messages
    """
    try:
        rag_chat_service = RagChatService(db)

        # Validate session exists
        if not rag_chat_service.validate_chat_session(uuid.UUID(session_id)):
            raise HTTPException(status_code=404, detail="Session not found")

        # Get conversation history
        history = rag_chat_service.get_conversation_history(
            uuid.UUID(session_id),
            limit=limit
        )

        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/chat/health")
async def chat_health():
    """
    Health check for the chat service.

    Returns:
        Health status
    """
    return {"status": "healthy", "component": "chat-service"}