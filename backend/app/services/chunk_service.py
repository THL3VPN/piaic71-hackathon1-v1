"""
Chunk service for the backend service.

This module provides CRUD operations for document chunks,
including creation, retrieval, updating, and deletion.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from ..models.chunk import Chunk


class ChunkService:
    """
    Service class for handling chunk operations.

    Provides methods for creating, retrieving, updating, and deleting chunks
    with proper error handling and validation.
    """

    @staticmethod
    def create_chunk(
        db: Session,
        document_id: uuid.UUID,
        chunk_index: int,
        chunk_text: str,
        chunk_hash: str,
        metadata: Optional[dict] = None,
        vector: Optional[list] = None
    ) -> Chunk:
        """
        Create a new chunk in the database.

        Args:
            db: Database session
            document_id: ID of the document this chunk belongs to
            chunk_index: Sequential index of the chunk within the document
            chunk_text: The actual content of the chunk
            chunk_hash: Hash for deduplication
            metadata: Optional metadata dictionary
            vector: Optional embedding vector

        Returns:
            Chunk: Created chunk instance

        Raises:
            IntegrityError: If a chunk with the same hash already exists
        """
        import json
        # Serialize vector to JSON string for database storage
        vector_json = json.dumps(vector) if vector is not None else None

        chunk = Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_text=chunk_text,
            chunk_hash=chunk_hash,
            vector=vector_json,
            metadata=metadata
        )
        db.add(chunk)
        try:
            db.commit()
            db.refresh(chunk)
            return chunk
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_chunk_by_id(db: Session, chunk_id: uuid.UUID) -> Optional[Chunk]:
        """
        Retrieve a chunk by its ID.

        Args:
            db: Database session
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk: Chunk instance if found, None otherwise
        """
        return db.query(Chunk).filter(Chunk.id == chunk_id).first()

    @staticmethod
    def get_chunks_by_document_id(db: Session, document_id: uuid.UUID) -> List[Chunk]:
        """
        Retrieve all chunks for a specific document, ordered by index.

        Args:
            db: Database session
            document_id: ID of the document to get chunks for

        Returns:
            List[Chunk]: List of chunk instances ordered by index
        """
        return db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.chunk_index).all()

    @staticmethod
    def get_chunk_by_hash(db: Session, chunk_hash: str) -> Optional[Chunk]:
        """
        Retrieve a chunk by its hash.

        Args:
            db: Database session
            chunk_hash: Hash of the chunk to retrieve

        Returns:
            Chunk: Chunk instance if found, None otherwise
        """
        return db.query(Chunk).filter(Chunk.chunk_hash == chunk_hash).first()

    @staticmethod
    def get_all_chunks(db: Session, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """
        Retrieve all chunks with pagination.

        Args:
            db: Database session
            skip: Number of chunks to skip (for pagination)
            limit: Maximum number of chunks to return

        Returns:
            List[Chunk]: List of chunk instances
        """
        return db.query(Chunk).offset(skip).limit(limit).all()

    @staticmethod
    def update_chunk(db: Session, chunk_id: uuid.UUID, **kwargs) -> Optional[Chunk]:
        """
        Update a chunk's attributes.

        Args:
            db: Database session
            chunk_id: ID of the chunk to update
            **kwargs: Attributes to update

        Returns:
            Chunk: Updated chunk instance if found, None otherwise
        """
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if chunk:
            for key, value in kwargs.items():
                if hasattr(chunk, key):
                    setattr(chunk, key, value)
            chunk.updated_at = __import__('datetime').datetime.utcnow()
            db.commit()
            db.refresh(chunk)
        return chunk

    @staticmethod
    def delete_chunk(db: Session, chunk_id: uuid.UUID) -> bool:
        """
        Delete a chunk by its ID.

        Args:
            db: Database session
            chunk_id: ID of the chunk to delete

        Returns:
            bool: True if chunk was deleted, False if not found
        """
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if chunk:
            db.delete(chunk)
            db.commit()
            return True
        return False

    @staticmethod
    def chunk_exists(db: Session, chunk_hash: str) -> bool:
        """
        Check if a chunk with the given hash exists.

        Args:
            db: Database session
            chunk_hash: Hash to check

        Returns:
            bool: True if chunk exists, False otherwise
        """
        return db.query(Chunk).filter(Chunk.chunk_hash == chunk_hash).count() > 0

    @staticmethod
    def get_chunks_count_by_document(db: Session, document_id: uuid.UUID) -> int:
        """
        Get the count of chunks for a specific document.

        Args:
            db: Database session
            document_id: ID of the document

        Returns:
            int: Number of chunks for the document
        """
        return db.query(Chunk).filter(Chunk.document_id == document_id).count()