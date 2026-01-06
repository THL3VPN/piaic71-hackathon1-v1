"""
Document operations tests for the backend service.

This module contains tests for document operations,
verifying that documents can be created, retrieved, updated, and deleted properly.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

# Import all models to ensure they're registered with Base metadata before creating tables
from app.models.document import Document
from app.services.document_service import DocumentService
from app.database.document_repository import DocumentRepository
from app.database.connection import Base

# Import the Base model's metadata to ensure tables are created properly


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    # Ensure all models are registered with Base metadata before creating tables
    # The Document model is already imported at the top of the file
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def test_document_creation(db_session):
    """Test that documents can be created successfully."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    document = DocumentService.create_document(
        db_session, source_path, title, checksum
    )

    assert document is not None
    assert document.source_path == source_path
    assert document.title == title
    assert document.checksum == checksum


def test_document_creation_with_uniqueness_check(db_session):
    """Test that document creation with uniqueness check works."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    # Create first document
    doc1 = DocumentService.create_document_with_uniqueness_check(
        db_session, source_path, title, checksum
    )
    assert doc1 is not None

    # Try to create another document with same source_path
    with pytest.raises(Exception):
        DocumentService.create_document_with_uniqueness_check(
            db_session, source_path, "Different Title", "different_checksum"
        )


def test_document_retrieval_by_id(db_session):
    """Test that documents can be retrieved by ID."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    created_doc = DocumentService.create_document(
        db_session, source_path, title, checksum
    )
    retrieved_doc = DocumentService.get_document_by_id(
        db_session, created_doc.id
    )

    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.source_path == created_doc.source_path
    assert retrieved_doc.title == created_doc.title


def test_document_retrieval_by_source_path(db_session):
    """Test that documents can be retrieved by source path."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    created_doc = DocumentService.create_document(
        db_session, source_path, title, checksum
    )
    retrieved_doc = DocumentService.get_document_by_source_path(
        db_session, source_path
    )

    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id
    assert retrieved_doc.source_path == created_doc.source_path
    assert retrieved_doc.title == created_doc.title


def test_document_does_not_exist(db_session):
    """Test that retrieving a non-existent document returns None."""
    import uuid
    non_existent_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
    retrieved_doc = DocumentService.get_document_by_id(
        db_session, non_existent_id
    )

    assert retrieved_doc is None

    retrieved_doc = DocumentService.get_document_by_source_path(
        db_session, "non/existent/path.md"
    )
    assert retrieved_doc is None


def test_document_update(db_session):
    """Test that documents can be updated."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    created_doc = DocumentService.create_document(
        db_session, source_path, title, checksum
    )

    new_title = "Updated Test Document"
    updated_doc = DocumentService.update_document(
        db_session, created_doc.id, title=new_title
    )

    assert updated_doc is not None
    assert updated_doc.title == new_title
    assert updated_doc.source_path == source_path


def test_document_deletion(db_session):
    """Test that documents can be deleted."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    created_doc = DocumentService.create_document(
        db_session, source_path, title, checksum
    )

    # Verify document exists
    retrieved_doc = DocumentService.get_document_by_id(
        db_session, created_doc.id
    )
    assert retrieved_doc is not None

    # Delete the document
    deleted = DocumentService.delete_document(db_session, created_doc.id)
    assert deleted is True

    # Verify document no longer exists
    retrieved_doc = DocumentService.get_document_by_id(
        db_session, created_doc.id
    )
    assert retrieved_doc is None


def test_document_exists(db_session):
    """Test that document existence check works."""
    source_path = "docs/test/document.md"
    title = "Test Document"
    checksum = "abc123"

    # Document should not exist initially
    exists = DocumentService.document_exists(db_session, source_path)
    assert exists is False

    # Create document
    DocumentService.create_document(db_session, source_path, title, checksum)

    # Document should now exist
    exists = DocumentService.document_exists(db_session, source_path)
    assert exists is True


def test_document_repository_pattern(db_session):
    """Test that the document repository pattern works correctly."""
    source_path = "docs/test/repository_test.md"
    title = "Repository Test Document"
    checksum = "repo123"

    # Create repository instance
    repo = DocumentRepository(db_session)

    # Create document via repository
    created_doc = repo.create(source_path, title, checksum)
    assert created_doc is not None
    assert created_doc.source_path == source_path

    # Retrieve document via repository
    retrieved_doc = repo.get_by_source_path(source_path)
    assert retrieved_doc is not None
    assert retrieved_doc.id == created_doc.id

    # Check if document exists via repository
    exists = repo.exists(source_path)
    assert exists is True

    # Get all documents (should have 1)
    all_docs = repo.get_all()
    assert len(all_docs) == 1

    # Update document via repository
    updated_doc = repo.update(created_doc.id, title="Updated via Repo")
    assert updated_doc is not None
    assert updated_doc.title == "Updated via Repo"

    # Delete document via repository
    deleted = repo.delete(created_doc.id)
    assert deleted is True

    # Verify deletion
    retrieved_doc = repo.get_by_id(created_doc.id)
    assert retrieved_doc is None