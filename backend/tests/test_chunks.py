"""
Chunk operations tests for the backend service.

This module contains tests for chunk operations,
verifying that chunks can be created, retrieved, updated, and deleted properly.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import uuid

from app.models.document import Document
from app.models.chunk import Chunk
from app.services.document_service import DocumentService
from app.services.chunk_service import ChunkService
from app.database.chunk_repository import ChunkRepository
from app.database.connection import Base


@pytest.fixture
def db_session():
    """Create a test database session."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:")
    # Ensure all models are registered with Base metadata before creating tables
    # Models are imported at the top of the file
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def test_chunk_creation(db_session):
    """Test that chunks can be created successfully."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_test.md", "Chunk Test Document", "chunk_test_checksum"
    )

    chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="This is a test chunk.",
        chunk_hash="chunk_hash_123",
        metadata={"headings": ["Test"]}
    )

    assert chunk is not None
    assert chunk.document_id == document.id
    assert chunk.chunk_index == 0
    assert chunk.chunk_text == "This is a test chunk."
    assert chunk.chunk_hash == "chunk_hash_123"
    assert chunk.metadata == {"headings": ["Test"]}


def test_chunk_retrieval_by_id(db_session):
    """Test that chunks can be retrieved by ID."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_retrieval.md", "Chunk Retrieval Test", "retrieval_checksum"
    )

    created_chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="Test chunk for retrieval.",
        chunk_hash="retrieval_hash_123"
    )

    retrieved_chunk = ChunkService.get_chunk_by_id(db_session, created_chunk.id)

    assert retrieved_chunk is not None
    assert retrieved_chunk.id == created_chunk.id
    assert retrieved_chunk.document_id == document.id
    assert retrieved_chunk.chunk_text == "Test chunk for retrieval."


def test_chunk_retrieval_by_document_id(db_session):
    """Test that all chunks for a document can be retrieved."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_doc.md", "Chunk Document Test", "doc_checksum"
    )

    # Create multiple chunks for the same document
    chunk1 = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="First chunk.",
        chunk_hash="hash_001"
    )
    chunk2 = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=1,
        chunk_text="Second chunk.",
        chunk_hash="hash_002"
    )
    chunk3 = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=2,
        chunk_text="Third chunk.",
        chunk_hash="hash_003"
    )

    chunks = ChunkService.get_chunks_by_document_id(db_session, document.id)

    assert len(chunks) == 3
    # Check that they are ordered by index
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2
    assert chunks[0].id == chunk1.id
    assert chunks[1].id == chunk2.id
    assert chunks[2].id == chunk3.id


def test_chunk_retrieval_by_hash(db_session):
    """Test that chunks can be retrieved by hash."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_hash.md", "Chunk Hash Test", "hash_checksum"
    )

    chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="Test chunk for hash retrieval.",
        chunk_hash="unique_hash_456"
    )

    retrieved_chunk = ChunkService.get_chunk_by_hash(db_session, "unique_hash_456")

    assert retrieved_chunk is not None
    assert retrieved_chunk.id == chunk.id
    assert retrieved_chunk.chunk_hash == "unique_hash_456"


def test_chunk_does_not_exist(db_session):
    """Test that retrieving a non-existent chunk returns None."""
    non_existent_id = uuid.uuid4()
    retrieved_chunk = ChunkService.get_chunk_by_id(db_session, non_existent_id)
    assert retrieved_chunk is None

    retrieved_chunk = ChunkService.get_chunk_by_hash(db_session, "non_existent_hash")
    assert retrieved_chunk is None


def test_chunk_update(db_session):
    """Test that chunks can be updated."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_update.md", "Chunk Update Test", "update_checksum"
    )

    chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="Original chunk text.",
        chunk_hash="update_hash_123"
    )

    updated_chunk = ChunkService.update_chunk(
        db_session, chunk.id, chunk_text="Updated chunk text.", chunk_index=5
    )

    assert updated_chunk is not None
    assert updated_chunk.chunk_text == "Updated chunk text."
    assert updated_chunk.chunk_index == 5


def test_chunk_deletion(db_session):
    """Test that chunks can be deleted."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_delete.md", "Chunk Delete Test", "delete_checksum"
    )

    chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="Chunk to be deleted.",
        chunk_hash="delete_hash_123"
    )

    # Verify chunk exists
    retrieved_chunk = ChunkService.get_chunk_by_id(db_session, chunk.id)
    assert retrieved_chunk is not None

    # Delete the chunk
    deleted = ChunkService.delete_chunk(db_session, chunk.id)
    assert deleted is True

    # Verify chunk no longer exists
    retrieved_chunk = ChunkService.get_chunk_by_id(db_session, chunk.id)
    assert retrieved_chunk is None


def test_chunk_exists(db_session):
    """Test that chunk existence check works."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_exists.md", "Chunk Exists Test", "exists_checksum"
    )

    chunk = ChunkService.create_chunk(
        db_session,
        document_id=document.id,
        chunk_index=0,
        chunk_text="Test chunk for existence check.",
        chunk_hash="exists_hash_789"
    )

    # Chunk should exist
    exists = ChunkService.chunk_exists(db_session, "exists_hash_789")
    assert exists is True

    # Non-existent chunk should not exist
    exists = ChunkService.chunk_exists(db_session, "non_existent_hash")
    assert exists is False


def test_chunk_repository_pattern(db_session):
    """Test that the chunk repository pattern works correctly."""
    # First create a document
    document = DocumentService.create_document(
        db_session, "docs/test/chunk_repo.md", "Chunk Repository Test", "repo_checksum"
    )

    # Create repository instance
    repo = ChunkRepository(db_session)

    # Create chunk via repository
    created_chunk = repo.create(
        document_id=document.id,
        chunk_index=0,
        chunk_text="Repository test chunk.",
        chunk_hash="repo_hash_abc",
        metadata={"source": "test"}
    )
    assert created_chunk is not None
    assert created_chunk.document_id == document.id

    # Retrieve chunk via repository
    retrieved_chunk = repo.get_by_id(created_chunk.id)
    assert retrieved_chunk is not None
    assert retrieved_chunk.id == created_chunk.id

    # Retrieve chunks by document
    chunks_by_doc = repo.get_by_document_id(document.id)
    assert len(chunks_by_doc) == 1
    assert chunks_by_doc[0].id == created_chunk.id

    # Check if chunk exists via repository
    exists = repo.exists("repo_hash_abc")
    assert exists is True

    # Get all chunks (should have 1)
    all_chunks = repo.get_all()
    assert len(all_chunks) == 1

    # Update chunk via repository
    updated_chunk = repo.update(created_chunk.id, chunk_text="Updated via Repo")
    assert updated_chunk is not None
    assert updated_chunk.chunk_text == "Updated via Repo"

    # Delete chunk via repository
    deleted = repo.delete(created_chunk.id)
    assert deleted is True

    # Verify deletion
    retrieved_chunk = repo.get_by_id(created_chunk.id)
    assert retrieved_chunk is None