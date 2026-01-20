"""
Ingestion job repository for the backend service.

This module provides data access operations for ingestion jobs,
implementing the repository pattern for ingestion-related operations.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..models.ingestion_job import IngestionJob
from ..services.ingestion_job_service import IngestionJobService


class IngestionJobRepository:
    """
    Repository class for ingestion job data access operations.

    Implements the repository pattern for ingestion-related database operations,
    providing methods to interact with ingestion data in a structured way.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        Args:
            db: Database session to use for operations
        """
        self.db = db

    def create_ingestion_job(
        self,
        document_id: uuid.UUID,
        status: str = "pending",
        total_chunks: Optional[int] = None,
        job_metadata: Optional[dict] = None
    ) -> IngestionJob:
        """
        Create a new ingestion job.

        Args:
            document_id: ID of the document being ingested
            status: Status of the ingestion job (pending, processing, completed, failed)
            total_chunks: Total number of chunks to process
            job_metadata: Additional metadata about the ingestion job

        Returns:
            IngestionJob: Created ingestion job instance
        """
        return IngestionJobService.create_ingestion_job(
            self.db, document_id, status, total_chunks, job_metadata
        )

    def get_ingestion_job_by_id(self, job_id: uuid.UUID) -> Optional[IngestionJob]:
        """
        Retrieve an ingestion job by its ID.

        Args:
            job_id: ID of the ingestion job to retrieve

        Returns:
            IngestionJob: Ingestion job instance if found, None otherwise
        """
        return IngestionJobService.get_ingestion_job_by_id(self.db, job_id)

    def get_ingestion_jobs_by_document_id(self, document_id: uuid.UUID) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs for a specific document, ordered by creation time.

        Args:
            document_id: ID of the document to get jobs for

        Returns:
            List[IngestionJob]: List of ingestion job instances ordered by creation time
        """
        return IngestionJobService.get_ingestion_jobs_by_document_id(self.db, document_id)

    def get_all_ingestion_jobs(self, skip: int = 0, limit: int = 100) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs with pagination.

        Args:
            skip: Number of jobs to skip (for pagination)
            limit: Maximum number of jobs to return

        Returns:
            List[IngestionJob]: List of ingestion job instances
        """
        return IngestionJobService.get_all_ingestion_jobs(self.db, skip, limit)

    def update_ingestion_job(self, job_id: uuid.UUID, **kwargs) -> Optional[IngestionJob]:
        """
        Update an ingestion job's attributes.

        Args:
            job_id: ID of the ingestion job to update
            **kwargs: Attributes to update

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.update_ingestion_job(self.db, job_id, **kwargs)

    def delete_ingestion_job(self, job_id: uuid.UUID) -> bool:
        """
        Delete an ingestion job by its ID.

        Args:
            job_id: ID of the ingestion job to delete

        Returns:
            bool: True if job was deleted, False if not found
        """
        return IngestionJobService.delete_ingestion_job(self.db, job_id)

    def ingestion_job_exists(self, job_id: uuid.UUID) -> bool:
        """
        Check if an ingestion job exists.

        Args:
            job_id: ID to check

        Returns:
            bool: True if job exists, False otherwise
        """
        return IngestionJobService.ingestion_job_exists(self.db, job_id)

    def get_ingestion_jobs_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs with a specific status, with pagination.

        Args:
            status: Status to filter by
            skip: Number of jobs to skip (for pagination)
            limit: Maximum number of jobs to return

        Returns:
            List[IngestionJob]: List of ingestion job instances with the specified status
        """
        return IngestionJobService.get_ingestion_jobs_by_status(self.db, status, skip, limit)

    def update_job_progress(self, job_id: uuid.UUID, processed_chunks: int, total_chunks: Optional[int] = None) -> Optional[IngestionJob]:
        """
        Update the progress of an ingestion job.

        Args:
            job_id: ID of the ingestion job to update
            processed_chunks: Number of chunks processed
            total_chunks: Total number of chunks (optional, can update separately)

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.update_job_progress(self.db, job_id, processed_chunks, total_chunks)

    def mark_job_completed(self, job_id: uuid.UUID) -> Optional[IngestionJob]:
        """
        Mark an ingestion job as completed.

        Args:
            job_id: ID of the ingestion job to mark as completed

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.mark_job_completed(self.db, job_id)

    def mark_job_failed(self, job_id: uuid.UUID, error_message: str) -> Optional[IngestionJob]:
        """
        Mark an ingestion job as failed with an error message.

        Args:
            job_id: ID of the ingestion job to mark as failed
            error_message: Error message to associate with the failure

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.mark_job_failed(self.db, job_id, error_message)

    def get_total_jobs_count(self) -> int:
        """
        Get the total count of ingestion jobs.

        Returns:
            int: Total number of ingestion jobs
        """
        return self.db.query(IngestionJob).count()

    def get_jobs_count_by_status(self, status: str) -> int:
        """
        Get the count of ingestion jobs with a specific status.

        Args:
            status: Status to count

        Returns:
            int: Number of ingestion jobs with the specified status
        """
        return self.db.query(IngestionJob).filter(IngestionJob.status == status).count()

    def get_jobs_count_by_document(self, document_id: uuid.UUID) -> int:
        """
        Get the count of ingestion jobs for a specific document.

        Args:
            document_id: ID of the document

        Returns:
            int: Number of ingestion jobs for the document
        """
        return self.db.query(IngestionJob).filter(IngestionJob.document_id == document_id).count()