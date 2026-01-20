"""
Document repository for the backend service.

This module provides data access operations for documents,
implementing the repository pattern for document-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.document import Document
from ..services.document_service import DocumentService


class DocumentRepository:
    """
    Repository class for document data access operations.

    Implements the repository pattern for document-related database operations,
    providing methods to interact with document data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create(self, source_path: str, title: str, checksum: str, content: str = None) -> Document:
        """
        Create a new document.

        Args:
            source_path: Document source path
            title: Document title
            checksum: Document checksum for change detection
            content: Document content (optional)

        Returns:
            Document: Created document instance
        """
        return DocumentService.create_document(self.db, source_path, title, checksum, content)

    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            document_id: ID of the document to retrieve

        Returns:
            Document: Document instance if found, None otherwise
        """
        return DocumentService.get_document_by_id(self.db, document_id)

    def get_by_source_path(self, source_path: str) -> Optional[Document]:
        """
        Retrieve a document by its source path.

        Args:
            source_path: Source path of the document to retrieve

        Returns:
            Document: Document instance if found, None otherwise
        """
        return DocumentService.get_document_by_source_path(self.db, source_path)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Retrieve all documents with pagination.

        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return

        Returns:
            List[Document]: List of document instances
        """
        return DocumentService.get_all_documents(self.db, skip, limit)

    def update(self, document_id: uuid.UUID, **kwargs) -> Optional[Document]:
        """
        Update a document's attributes.

        Args:
            document_id: ID of the document to update
            **kwargs: Attributes to update

        Returns:
            Document: Updated document instance if found, None otherwise
        """
        return DocumentService.update_document(self.db, document_id, **kwargs)

    def delete(self, document_id: uuid.UUID) -> bool:
        """
        Delete a document by its ID.

        Args:
            document_id: ID of the document to delete

        Returns:
            bool: True if document was deleted, False if not found
        """
        return DocumentService.delete_document(self.db, document_id)

    def exists(self, source_path: str) -> bool:
        """
        Check if a document with the given source path exists.

        Args:
            source_path: Source path to check

        Returns:
            bool: True if document exists, False otherwise
        """
        return DocumentService.document_exists(self.db, source_path)

    def get_count(self) -> int:
        """
        Get the total count of documents.

        Returns:
            int: Total number of documents
        """
        return self.db.query(Document).count()

    def find_by_checksum(self, checksum: str) -> Optional[Document]:
        """
        Find a document by its checksum.

        Args:
            checksum: Checksum to search for

        Returns:
            Document: Document instance if found, None otherwise
        """
        return self.db.query(Document).filter(Document.checksum == checksum).first()