"""
Initialization module for database models in the backend service.

This module provides imports for all database models to enable
easy access from other parts of the application.
"""
# Import base model first
from ..database.connection import Base

# Import all models
from .document import Document

# Import models that will be created later (for now, document, chunk exist)
from .chunk import Chunk
from .chat_session import ChatSession
from .chat_message import ChatMessage
from .ingestion_job import IngestionJob
from .query import Query
from .retrieval_result import RetrievalResult
from .context_bundle import ContextBundle
from .citation import Citation

# Define what gets imported with "from app.models import *"
__all__ = [
    "Base",
    "Document",
    "Chunk",
    "ChatSession",
    "ChatMessage",
    "IngestionJob",
    "Query",
    "RetrievalResult",
    "ContextBundle",
    "Citation"
]