"""
Document service for the backend service.

This module provides CRUD operations for documents,
including creation, retrieval, updating, and deletion.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid

from ..models.document import Document


class DocumentService:
    """
    Service class for handling document operations.

    Provides methods for creating, retrieving, updating, and deleting documents
    with proper error handling and validation.
    """

    @staticmethod
    def create_document(db: Session, source_path: str, title: str, checksum: str, content: str = None) -> Document:
        """
        Create a new document in the database.

        Args:
            db: Database session
            source_path: Document source path
            title: Document title
            checksum: Document checksum for change detection
            content: Document content (optional)

        Returns:
            Document: Created document instance

        Raises:
            IntegrityError: If a document with the same source_path already exists
        """
        document = Document(
            source_path=source_path,
            title=title,
            checksum=checksum,
            content=content
        )
        db.add(document)
        try:
            db.commit()
            db.refresh(document)
            return document
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_document_by_id(db: Session, document_id: uuid.UUID) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            db: Database session
            document_id: ID of the document to retrieve

        Returns:
            Document: Document instance if found, None otherwise
        """
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_document_by_source_path(db: Session, source_path: str) -> Optional[Document]:
        """
        Retrieve a document by its source path.

        Args:
            db: Database session
            source_path: Source path of the document to retrieve

        Returns:
            Document: Document instance if found, None otherwise
        """
        return db.query(Document).filter(Document.source_path == source_path).first()

    @staticmethod
    def get_all_documents(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
        """
        Retrieve all documents with pagination.

        Args:
            db: Database session
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return

        Returns:
            List[Document]: List of document instances
        """
        return db.query(Document).offset(skip).limit(limit).all()

    @staticmethod
    def update_document(db: Session, document_id: uuid.UUID, **kwargs) -> Optional[Document]:
        """
        Update a document's attributes.

        Args:
            db: Database session
            document_id: ID of the document to update
            **kwargs: Attributes to update

        Returns:
            Document: Updated document instance if found, None otherwise
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            for key, value in kwargs.items():
                if hasattr(document, key):
                    setattr(document, key, value)
            document.updated_at = __import__('datetime').datetime.utcnow()
            db.commit()
            db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: uuid.UUID) -> bool:
        """
        Delete a document by its ID.

        Args:
            db: Database session
            document_id: ID of the document to delete

        Returns:
            bool: True if document was deleted, False if not found
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
            return True
        return False

    @staticmethod
    def document_exists(db: Session, source_path: str) -> bool:
        """
        Check if a document with the given source path exists.

        Args:
            db: Database session
            source_path: Source path to check

        Returns:
            bool: True if document exists, False otherwise
        """
        return db.query(Document).filter(Document.source_path == source_path).count() > 0

    @staticmethod
    def create_document_with_uniqueness_check(db: Session, source_path: str, title: str, checksum: str) -> Document:
        """
        Create a new document with explicit source_path uniqueness check.

        Args:
            db: Database session
            source_path: Document source path
            title: Document title
            checksum: Document checksum for change detection

        Returns:
            Document: Created document instance

        Raises:
            IntegrityError: If a document with the same source_path already exists
        """
        # Check if document already exists with the same source_path
        existing_doc = db.query(Document).filter(Document.source_path == source_path).first()
        if existing_doc:
            raise IntegrityError(
                statement="INSERT",
                params={"source_path": source_path},
                orig=f"Document with source_path '{source_path}' already exists"
            )

        # Create new document
        document = Document(
            source_path=source_path,
            title=title,
            checksum=checksum
        )
        db.add(document)
        try:
            db.commit()
            db.refresh(document)
            return document
        except IntegrityError as e:
            db.rollback()
            raise e