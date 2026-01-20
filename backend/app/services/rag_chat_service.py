"""
RAG-integrated chat service for the backend service.

This module provides the core business logic for RAG-enhanced chat functionality,
integrating document retrieval with conversational capabilities.
"""
from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
import logging
import os

from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.services.chat_session_service import ChatSessionService
from app.services.chat_message_service import ChatMessageService
from app.services.retrieval_service import RetrievalService
from app.services.qdrant_service import QdrantService
from app.utils.citation_formatter import format_citations_from_chunks
from app.utils.hallucination_guard import HallucinationGuard
from app.services.llm_service import LLMService


logger = logging.getLogger(__name__)


class RagChatService:
    """
    Service class for RAG-integrated chat functionality.

    Orchestrates the complete RAG chat pipeline: receives user queries,
    retrieves relevant document chunks, builds contextual responses,
    and ensures grounding in actual book content to prevent hallucination.
    """

    def __init__(self, db: Session):
        """
        Initialize the RAG chat service.

        Args:
            db: Database session for data access
        """
        self.db = db
        self.chat_session_service = ChatSessionService()
        self.chat_message_service = ChatMessageService()
        self.retrieval_service = RetrievalService(db)
        self.qdrant_service = QdrantService()
        self.hallucination_guard = HallucinationGuard()

        # Initialize LLM service based on environment configuration
        provider_type = os.getenv("LLM_PROVIDER", "openai")  # Default to OpenAI
        # Pass the environment variable directly to ensure it's available
        self.llm_service = LLMService(
            provider_type=provider_type,
            api_key=os.getenv("OPENAI_API_KEY") if provider_type.lower() == "openai" else None
        )

    def process_chat_query(
        self,
        message: str,
        session_id: Optional[uuid.UUID] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Process a chat query through the RAG pipeline.

        Args:
            message: User's question/message
            session_id: Optional session ID (creates new if not provided)
            top_k: Number of top results to retrieve
            similarity_threshold: Minimum similarity score for inclusion

        Returns:
            Dictionary with response, citations, and session information
        """
        # Get or create session
        if session_id:
            session = self.chat_session_service.get_session_by_id(self.db, session_id)
            if not session:
                # Create new session if provided ID doesn't exist
                session = self.chat_session_service.create_session(self.db, metadata=None)
        else:
            # Create new session
            session = self.chat_session_service.create_session(self.db, metadata=None)

        # Save user message to session
        user_message = self.chat_message_service.create_message(
            self.db,
            session.session_id,
            "user",
            message
        )

        # Retrieve relevant chunks from documents
        try:
            retrieved_chunks = self.retrieval_service.retrieve_and_rank_chunks(
                question=message,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            # Return error response if retrieval fails
            response_message = self.chat_message_service.create_message(
                self.db,
                session.session_id,
                "assistant",
                "Sorry, I'm having trouble accessing the document repository right now."
            )
            return {
                "session_id": str(session.session_id),
                "answer": "Sorry, I'm having trouble accessing the document repository right now.",
                "citations": [],
                "error": str(e)
            }

        # Check if we have any retrieved results
        if not retrieved_chunks:
            # Respond with insufficient information message if no chunks were retrieved
            response_text = "I don't have sufficient information in the book content to answer this question."
            citations = []
        else:
            # Build context from retrieved chunks
            context_chunks = []
            for chunk in retrieved_chunks:
                content = getattr(chunk, 'content', getattr(chunk, 'chunk_text', ''))
                source_path = getattr(chunk, 'source_path', getattr(chunk, 'source_doc_path', ''))
                title = getattr(chunk, 'title', '')
                chunk_index = getattr(chunk, 'chunk_index', getattr(chunk, 'index', 0))

                chunk_data = {
                    'content': content,
                    'metadata': {
                        'source_path': source_path,
                        'title': title,
                        'chunk_index': chunk_index
                    }
                }
                context_chunks.append(chunk_data)

            # Generate response using LLM with the retrieved context
            try:
                response_data = self.llm_service.generate_answer_with_context(
                    question=message,
                    context_chunks=context_chunks
                )
                response_text = response_data['answer']
                citations = response_data['citations']
            except Exception as e:
                logger.error(f"Error generating LLM response: {e}")
                # Fallback to a simple response if LLM fails
                context_preview = " ".join([chunk['content'][:100] for chunk in context_chunks[:2]])
                response_text = f"Based on the book content: {context_preview}..."
                citations = format_citations_from_chunks(context_chunks)

            # Verify the response is grounded in the provided context
            if not self.hallucination_guard.is_answer_properly_grounded(response_text, " ".join([chunk['content'] for chunk in context_chunks])):
                response_text = "I found relevant information but cannot generate a properly grounded response."
                citations = []

        # Save assistant response to session
        assistant_message = self.chat_message_service.create_message(
            self.db,
            session.session_id,
            "assistant",
            response_text
        )

        return {
            "session_id": str(session.session_id),
            "answer": response_text,
            "citations": citations,
            "retrieved_chunks_count": len(retrieved_chunks) if retrieved_chunks else 0
        }

    def get_conversation_history(self, session_id: uuid.UUID, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: ID of the session to retrieve history for
            limit: Maximum number of messages to return

        Returns:
            List of message dictionaries in chronological order
        """
        messages = self.chat_message_service.get_messages_by_session_id(self.db, session_id)

        # Limit the number of messages returned
        if limit and len(messages) > limit:
            messages = messages[-limit:]  # Get the most recent messages

        return [msg.to_dict() for msg in messages]

    def validate_chat_session(self, session_id: uuid.UUID) -> bool:
        """
        Validate that a chat session exists and is active.

        Args:
            session_id: ID of the session to validate

        Returns:
            True if session exists and is valid, False otherwise
        """
        return self.chat_session_service.session_exists(self.db, session_id)

    def get_session_stats(self, session_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get statistics for a chat session.

        Args:
            session_id: ID of the session to get stats for

        Returns:
            Dictionary with session statistics
        """
        session = self.chat_session_service.get_session_by_id(self.db, session_id)
        if not session:
            return {}

        message_count = self.chat_message_service.get_messages_count_by_session(self.db, session_id)

        return {
            "session_id": str(session_id),
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "message_count": message_count,
            "last_activity": session.updated_at.isoformat() if session.updated_at else None
        }