"""
Chunk repository for the backend service.

This module provides data access operations for chunks,
implementing the repository pattern for chunk-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.chunk import Chunk
from ..services.chunk_service import ChunkService


class ChunkRepository:
    """
    Repository class for chunk data access operations.

    Implements the repository pattern for chunk-related database operations,
    providing methods to interact with chunk data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create(
        self,
        document_id: uuid.UUID,
        chunk_index: int,
        chunk_text: str,
        chunk_hash: str,
        metadata: Optional[dict] = None,
        vector: Optional[list] = None
    ) -> Chunk:
        """
        Create a new chunk.

        Args:
            document_id: ID of the document this chunk belongs to
            chunk_index: Sequential index of the chunk within the document
            chunk_text: The actual content of the chunk
            chunk_hash: Hash for deduplication
            metadata: Optional metadata dictionary
            vector: Optional embedding vector

        Returns:
            Chunk: Created chunk instance
        """
        return ChunkService.create_chunk(
            self.db, document_id, chunk_index, chunk_text, chunk_hash, metadata, vector
        )

    def get_by_id(self, chunk_id: uuid.UUID) -> Optional[Chunk]:
        """
        Retrieve a chunk by its ID.

        Args:
            chunk_id: ID of the chunk to retrieve

        Returns:
            Chunk: Chunk instance if found, None otherwise
        """
        return ChunkService.get_chunk_by_id(self.db, chunk_id)

    def get_by_hash(self, chunk_hash: str) -> Optional[Chunk]:
        """
        Retrieve a chunk by its hash.

        Args:
            chunk_hash: Hash of the chunk to retrieve

        Returns:
            Chunk: Chunk instance if found, None otherwise
        """
        return ChunkService.get_chunk_by_hash(self.db, chunk_hash)

    def get_by_document_id(self, document_id: uuid.UUID) -> List[Chunk]:
        """
        Retrieve all chunks for a specific document, ordered by index.

        Args:
            document_id: ID of the document to get chunks for

        Returns:
            List[Chunk]: List of chunk instances ordered by index
        """
        return ChunkService.get_chunks_by_document_id(self.db, document_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """
        Retrieve all chunks with pagination.

        Args:
            skip: Number of chunks to skip (for pagination)
            limit: Maximum number of chunks to return

        Returns:
            List[Chunk]: List of chunk instances
        """
        return ChunkService.get_all_chunks(self.db, skip, limit)

    def update(self, chunk_id: uuid.UUID, **kwargs) -> Optional[Chunk]:
        """
        Update a chunk's attributes.

        Args:
            chunk_id: ID of the chunk to update
            **kwargs: Attributes to update

        Returns:
            Chunk: Updated chunk instance if found, None otherwise
        """
        return ChunkService.update_chunk(self.db, chunk_id, **kwargs)

    def delete(self, chunk_id: uuid.UUID) -> bool:
        """
        Delete a chunk by its ID.

        Args:
            chunk_id: ID of the chunk to delete

        Returns:
            bool: True if chunk was deleted, False if not found
        """
        return ChunkService.delete_chunk(self.db, chunk_id)

    def exists(self, chunk_hash: str) -> bool:
        """
        Check if a chunk with the given hash exists.

        Args:
            chunk_hash: Hash to check

        Returns:
            bool: True if chunk exists, False otherwise
        """
        return ChunkService.chunk_exists(self.db, chunk_hash)

    def get_count_by_document(self, document_id: uuid.UUID) -> int:
        """
        Get the count of chunks for a specific document.

        Args:
            document_id: ID of the document

        Returns:
            int: Number of chunks for the document
        """
        return ChunkService.get_chunks_count_by_document(self.db, document_id)

    def get_count(self) -> int:
        """
        Get the total count of chunks.

        Returns:
            int: Total number of chunks
        """
        return self.db.query(Chunk).count()