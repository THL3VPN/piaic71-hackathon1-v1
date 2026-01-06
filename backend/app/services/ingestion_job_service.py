"""
Ingestion job service for the backend service.

This module provides CRUD operations for ingestion jobs,
including creation, retrieval, updating, and deletion.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from datetime import datetime
import json

from ..models.ingestion_job import IngestionJob


class IngestionJobService:
    """
    Service class for handling ingestion job operations.

    Provides methods for creating, retrieving, updating, and deleting ingestion jobs
    with proper error handling and validation.
    """

    @staticmethod
    def create_ingestion_job(
        db: Session,
        document_id: uuid.UUID,
        status: str = "pending",
        total_chunks: Optional[int] = None,
        job_metadata: Optional[dict] = None
    ) -> IngestionJob:
        """
        Create a new ingestion job in the database.

        Args:
            db: Database session
            document_id: ID of the document being ingested
            status: Status of the ingestion job (pending, processing, completed, failed)
            total_chunks: Total number of chunks to process
            job_metadata: Additional metadata about the ingestion job

        Returns:
            IngestionJob: Created ingestion job instance
        """
        # Validate status
        valid_statuses = ["pending", "processing", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")

        # Validate progress range if provided
        if total_chunks is not None and total_chunks < 0:
            raise ValueError("Total chunks must be non-negative")

        # Serialize job_metadata to JSON string for SQLite compatibility
        serialized_job_metadata = json.dumps(job_metadata) if job_metadata else None

        job = IngestionJob(
            document_id=document_id,
            status=status,
            total_chunks=total_chunks,
            job_metadata=serialized_job_metadata
        )
        db.add(job)
        try:
            db.commit()
            db.refresh(job)
            return job
        except IntegrityError as e:
            db.rollback()
            raise e

    @staticmethod
    def get_ingestion_job_by_id(db: Session, job_id: uuid.UUID) -> Optional[IngestionJob]:
        """
        Retrieve an ingestion job by its ID.

        Args:
            db: Database session
            job_id: ID of the ingestion job to retrieve

        Returns:
            IngestionJob: Ingestion job instance if found, None otherwise
        """
        return db.query(IngestionJob).filter(IngestionJob.id == job_id).first()

    @staticmethod
    def get_ingestion_jobs_by_document_id(db: Session, document_id: uuid.UUID) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs for a specific document, ordered by creation time.

        Args:
            db: Database session
            document_id: ID of the document to get jobs for

        Returns:
            List[IngestionJob]: List of ingestion job instances ordered by creation time
        """
        return db.query(IngestionJob).filter(
            IngestionJob.document_id == document_id
        ).order_by(IngestionJob.created_at).all()

    @staticmethod
    def get_all_ingestion_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs with pagination.

        Args:
            db: Database session
            skip: Number of jobs to skip (for pagination)
            limit: Maximum number of jobs to return

        Returns:
            List[IngestionJob]: List of ingestion job instances
        """
        return db.query(IngestionJob).offset(skip).limit(limit).all()

    @staticmethod
    def update_ingestion_job(db: Session, job_id: uuid.UUID, **kwargs) -> Optional[IngestionJob]:
        """
        Update an ingestion job's attributes.

        Args:
            db: Database session
            job_id: ID of the ingestion job to update
            **kwargs: Attributes to update

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            for key, value in kwargs.items():
                if hasattr(job, key):
                    # Validate status if being updated
                    if key == "status" and value not in ["pending", "processing", "completed", "failed"]:
                        raise ValueError(f"Status must be one of ['pending', 'processing', 'completed', 'failed']")

                    # Validate progress if being updated
                    if key == "progress" and (value < 0 or value > 100):
                        raise ValueError("Progress must be between 0 and 100")

                    # Validate total_chunks if being updated
                    if key == "total_chunks" and value is not None and value < 0:
                        raise ValueError("Total chunks must be non-negative")

                    # Serialize job_metadata to JSON string for SQLite compatibility
                    if key == "job_metadata":
                        value = json.dumps(value) if value else None

                    setattr(job, key, value)

            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)
        return job

    @staticmethod
    def delete_ingestion_job(db: Session, job_id: uuid.UUID) -> bool:
        """
        Delete an ingestion job by its ID.

        Args:
            db: Database session
            job_id: ID of the ingestion job to delete

        Returns:
            bool: True if job was deleted, False if not found
        """
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            db.delete(job)
            db.commit()
            return True
        return False

    @staticmethod
    def ingestion_job_exists(db: Session, job_id: uuid.UUID) -> bool:
        """
        Check if an ingestion job with the given ID exists.

        Args:
            db: Database session
            job_id: ID to check

        Returns:
            bool: True if job exists, False otherwise
        """
        return db.query(IngestionJob).filter(IngestionJob.id == job_id).count() > 0

    @staticmethod
    def get_ingestion_jobs_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[IngestionJob]:
        """
        Retrieve all ingestion jobs with a specific status, with pagination.

        Args:
            db: Database session
            status: Status to filter by
            skip: Number of jobs to skip (for pagination)
            limit: Maximum number of jobs to return

        Returns:
            List[IngestionJob]: List of ingestion job instances with the specified status
        """
        return db.query(IngestionJob).filter(IngestionJob.status == status).offset(skip).limit(limit).all()

    @staticmethod
    def update_job_progress(db: Session, job_id: uuid.UUID, processed_chunks: int, total_chunks: Optional[int] = None) -> Optional[IngestionJob]:
        """
        Update the progress of an ingestion job.

        Args:
            db: Database session
            job_id: ID of the ingestion job to update
            processed_chunks: Number of chunks processed
            total_chunks: Total number of chunks (optional, can update separately)

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.processed_chunks = processed_chunks
            if total_chunks is not None:
                job.total_chunks = total_chunks

            # Calculate progress percentage
            if job.total_chunks and job.total_chunks > 0:
                job.progress = min(100, int((job.processed_chunks / job.total_chunks) * 100))
            else:
                job.progress = 0

            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)
        return job

    @staticmethod
    def mark_job_completed(db: Session, job_id: uuid.UUID) -> Optional[IngestionJob]:
        """
        Mark an ingestion job as completed.

        Args:
            db: Database session
            job_id: ID of the ingestion job to mark as completed

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.update_ingestion_job(db, job_id, status="completed", progress=100)

    @staticmethod
    def mark_job_failed(db: Session, job_id: uuid.UUID, error_message: str) -> Optional[IngestionJob]:
        """
        Mark an ingestion job as failed with an error message.

        Args:
            db: Database session
            job_id: ID of the ingestion job to mark as failed
            error_message: Error message to associate with the failure

        Returns:
            IngestionJob: Updated ingestion job instance if found, None otherwise
        """
        return IngestionJobService.update_ingestion_job(db, job_id, status="failed", error_message=error_message)