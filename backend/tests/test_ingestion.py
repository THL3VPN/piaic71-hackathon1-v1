"""
Ingestion job operations tests for the backend service.

This module contains tests for ingestion job operations,
verifying that ingestion jobs can be created, retrieved, updated, and deleted properly,
and that job status and progress tracking works correctly.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import uuid
from datetime import datetime

from app.models.ingestion_job import IngestionJob
from app.models.document import Document
from app.services.ingestion_job_service import IngestionJobService
from app.services.document_service import DocumentService
from app.database.ingestion_job_repository import IngestionJobRepository
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


def test_ingestion_job_creation(db_session):
    """Test that ingestion jobs can be created successfully."""
    # Create a document first to associate with the job
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending",
        total_chunks=10,
        job_metadata={"source_format": "pdf", "parser": "pymupdf"}
    )

    assert job is not None
    assert job.id is not None
    assert job.document_id == document.id
    assert job.status == "pending"
    assert job.total_chunks == 10
    assert job.parsed_job_metadata == {"source_format": "pdf", "parser": "pymupdf"}
    assert job.created_at is not None
    assert job.updated_at is not None


def test_ingestion_job_retrieval_by_id(db_session):
    """Test that ingestion jobs can be retrieved by ID."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    created_job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing"
    )

    retrieved_job = IngestionJobService.get_ingestion_job_by_id(db_session, created_job.id)

    assert retrieved_job is not None
    assert retrieved_job.id == created_job.id
    assert retrieved_job.document_id == document.id
    assert retrieved_job.status == "processing"
    assert retrieved_job.created_at == created_job.created_at


def test_ingestion_job_does_not_exist(db_session):
    """Test that retrieving a non-existent ingestion job returns None."""
    non_existent_id = uuid.uuid4()
    retrieved_job = IngestionJobService.get_ingestion_job_by_id(db_session, non_existent_id)
    assert retrieved_job is None


def test_ingestion_job_update(db_session):
    """Test that ingestion jobs can be updated."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending",
        total_chunks=5
    )

    updated_job = IngestionJobService.update_ingestion_job(
        db_session,
        job.id,
        status="processing",
        total_chunks=10
    )

    assert updated_job is not None
    assert updated_job.id == job.id
    assert updated_job.status == "processing"
    assert updated_job.total_chunks == 10


def test_ingestion_job_deletion(db_session):
    """Test that ingestion jobs can be deleted."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending"
    )

    # Verify job exists
    retrieved_job = IngestionJobService.get_ingestion_job_by_id(db_session, job.id)
    assert retrieved_job is not None

    # Delete the job
    deleted = IngestionJobService.delete_ingestion_job(db_session, job.id)
    assert deleted is True

    # Verify job no longer exists
    retrieved_job = IngestionJobService.get_ingestion_job_by_id(db_session, job.id)
    assert retrieved_job is None


def test_ingestion_job_exists(db_session):
    """Test that ingestion job existence check works."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending"
    )

    # Job should exist
    exists = IngestionJobService.ingestion_job_exists(db_session, job.id)
    assert exists is True

    # Non-existent job should not exist
    exists = IngestionJobService.ingestion_job_exists(db_session, uuid.uuid4())
    assert exists is False


def test_ingestion_jobs_by_document(db_session):
    """Test that all ingestion jobs for a document can be retrieved."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    # Create multiple jobs for the same document
    job1 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending"
    )
    job2 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing"
    )
    job3 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="completed"
    )

    jobs = IngestionJobService.get_ingestion_jobs_by_document_id(db_session, document.id)

    assert len(jobs) == 3
    # Check that they are ordered by creation time (first job first)
    assert jobs[0].id == job1.id
    assert jobs[1].id == job2.id
    assert jobs[2].id == job3.id
    assert jobs[0].status == "pending"
    assert jobs[1].status == "processing"
    assert jobs[2].status == "completed"


def test_ingestion_jobs_by_status(db_session):
    """Test that ingestion jobs can be retrieved by status."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    # Create jobs with different statuses
    job1 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending"
    )
    job2 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing"
    )
    job3 = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="pending"
    )

    pending_jobs = IngestionJobService.get_ingestion_jobs_by_status(db_session, "pending")
    processing_jobs = IngestionJobService.get_ingestion_jobs_by_status(db_session, "processing")

    assert len(pending_jobs) == 2
    assert len(processing_jobs) == 1
    assert pending_jobs[0].id in [job1.id, job3.id]
    assert processing_jobs[0].id == job2.id


def test_update_job_progress(db_session):
    """Test that job progress can be updated correctly."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing",
        total_chunks=10
    )

    # Update progress
    updated_job = IngestionJobService.update_job_progress(db_session, job.id, 5, 10)

    assert updated_job is not None
    assert updated_job.processed_chunks == 5
    assert updated_job.total_chunks == 10
    assert updated_job.progress == 50  # 5/10 = 50%

    # Update progress again
    updated_job = IngestionJobService.update_job_progress(db_session, job.id, 8)

    assert updated_job.processed_chunks == 8
    # total_chunks should remain 10 since we didn't update it
    assert updated_job.total_chunks == 10
    assert updated_job.progress == 80  # 8/10 = 80%


def test_mark_job_completed(db_session):
    """Test that jobs can be marked as completed."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing"
    )

    completed_job = IngestionJobService.mark_job_completed(db_session, job.id)

    assert completed_job is not None
    assert completed_job.status == "completed"
    assert completed_job.progress == 100


def test_mark_job_failed(db_session):
    """Test that jobs can be marked as failed with error messages."""
    # Create a document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    job = IngestionJobService.create_ingestion_job(
        db_session,
        document_id=document.id,
        status="processing"
    )

    failed_job = IngestionJobService.mark_job_failed(db_session, job.id, "File format not supported")

    assert failed_job is not None
    assert failed_job.status == "failed"
    assert failed_job.error_message == "File format not supported"


def test_ingestion_job_repository_pattern(db_session):
    """Test that the ingestion job repository pattern works correctly."""
    # Create document first
    document = DocumentService.create_document(
        db_session,
        source_path="/path/to/test/document.pdf",
        title="Test Document",
        checksum="abc123"
    )

    # Create repository instance
    repo = IngestionJobRepository(db_session)

    # Create job via repository
    created_job = repo.create_ingestion_job(
        document_id=document.id,
        status="pending",
        total_chunks=5,
        job_metadata={"test": True}
    )
    assert created_job is not None
    assert created_job.id is not None
    assert created_job.document_id == document.id
    assert created_job.status == "pending"
    assert created_job.total_chunks == 5
    assert created_job.parsed_job_metadata == {"test": True}

    # Retrieve job via repository
    retrieved_job = repo.get_ingestion_job_by_id(created_job.id)
    assert retrieved_job is not None
    assert retrieved_job.id == created_job.id

    # Retrieve jobs by document via repository
    jobs_by_document = repo.get_ingestion_jobs_by_document_id(document.id)
    assert len(jobs_by_document) == 1
    assert jobs_by_document[0].id == created_job.id

    # Update job via repository
    updated_job = repo.update_ingestion_job(created_job.id, status="processing", total_chunks=10)
    assert updated_job is not None
    assert updated_job.status == "processing"
    assert updated_job.total_chunks == 10

    # Update job progress via repository
    progress_job = repo.update_job_progress(created_job.id, 5, 10)
    assert progress_job is not None
    assert progress_job.processed_chunks == 5
    assert progress_job.progress == 50

    # Mark job completed via repository
    completed_job = repo.mark_job_completed(created_job.id)
    assert completed_job is not None
    assert completed_job.status == "completed"

    # Create another job to test status filtering
    job2 = repo.create_ingestion_job(document_id=document.id, status="failed")
    failed_jobs = repo.get_ingestion_jobs_by_status("failed")
    assert len(failed_jobs) == 1
    assert failed_jobs[0].id == job2.id

    # Check if job exists via repository
    exists = repo.ingestion_job_exists(created_job.id)
    assert exists is True

    # Get counts
    total_count = repo.get_total_jobs_count()
    assert total_count == 2  # We created 2 jobs

    status_count = repo.get_jobs_count_by_status("completed")
    assert status_count == 1

    doc_count = repo.get_jobs_count_by_document(document.id)
    assert doc_count == 2

    # Delete job via repository
    deleted = repo.delete_ingestion_job(created_job.id)
    assert deleted is True

    # Verify deletion
    retrieved_job = repo.get_ingestion_job_by_id(created_job.id)
    assert retrieved_job is None