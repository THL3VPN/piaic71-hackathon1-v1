"""
Core ingestion service that orchestrates the document ingestion pipeline.
"""
import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console

from app.config import settings
from app.utils.text_extractor import extract_text_with_frontmatter
from app.utils.chunker import chunk_document, Chunk
from app.utils.checksum import calculate_sha256
from app.database.document_repository import DocumentRepository
from app.database.chunk_repository import ChunkRepository
from app.database.ingestion_job_repository import IngestionJobRepository
from app.services.qdrant_service import qdrant_service
from app.models.document import Document
from app.models.chunk import Chunk as ChunkModel


logger = logging.getLogger(__name__)
console = Console()


class IngestionService:
    """Service to handle the complete document ingestion pipeline."""

    def __init__(self, db_session: Session):
        """
        Initialize the ingestion service.

        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.document_repo = DocumentRepository(db_session)
        self.chunk_repo = ChunkRepository(db_session)
        self.ingestion_job_repo = IngestionJobRepository(db_session)

    def scan_documents_directory(self, directory_path: str = None) -> List[str]:
        """
        Scan the documents directory for supported file types.

        Args:
            directory_path: Path to scan (defaults to configured source directory)

        Returns:
            List of file paths found
        """
        if directory_path is None:
            directory_path = settings.source_directory

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Source directory does not exist: {directory_path}")

        files = []
        for ext in settings.supported_extensions:
            files.extend(directory.rglob(f"*{ext}"))

        return [str(f) for f in files]

    def process_document(self, file_path: str) -> Tuple[Document, List[ChunkModel]]:
        """
        Process a single document: extract text, chunk, store in database, and upsert to Qdrant.

        Args:
            file_path: Path to the document file

        Returns:
            Tuple of (Document, List of ChunkModels)
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Calculate checksum
        checksum = calculate_sha256(content)

        # Check if document with same checksum already exists (for incremental ingestion)
        existing_doc = self.document_repo.find_by_checksum(checksum)
        if existing_doc:
            logger.info(f"Document with checksum {checksum} already exists, skipping: {file_path}")
            return existing_doc, []

        # Extract text and metadata
        clean_content, frontmatter, title = extract_text_with_frontmatter(content)

        if not title:
            # Generate title from filename if not found in content
            title = Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()

        # Create or update document in database
        relative_path = str(Path(file_path).relative_to(settings.source_directory))
        document = self.document_repo.create(
            source_path=relative_path,
            title=title,
            checksum=checksum,
            content=clean_content
        )

        # Chunk the document
        chunks = chunk_document(clean_content, str(document.id))

        # Process and store chunks
        chunk_models = []
        for chunk in chunks:
            # Compute embedding first
            embedding = self.compute_embedding(chunk.content)

            # Create chunk in database with vector
            chunk_model = self.chunk_repo.create(
                document_id=document.id,
                chunk_index=chunk.index,
                chunk_text=chunk.content,
                chunk_hash=chunk.id,
                vector=embedding,  # Store the vector in the database
                metadata=None  # Add metadata if needed
            )
            chunk_models.append(chunk_model)

            # Upsert chunk to Qdrant
            try:
                # Upsert to Qdrant
                qdrant_service.upsert_point(
                    chunk_id=chunk.id,
                    vector=embedding,
                    payload={
                        'document_id': str(document.id),
                        'source_path': relative_path,
                        'title': title,
                        'chunk_index': chunk.index,
                        'content': chunk.content
                    }
                )
            except Exception as e:
                logger.error(f"Failed to upsert chunk {chunk.id} to Qdrant: {e}")
                # Continue processing other chunks even if Qdrant fails

        return document, chunk_models

    def compute_embedding(self, text: str) -> List[float]:
        """
        Compute embedding for text using the real embedding service.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        # Initialize embedding service to compute real embeddings
        from .embedding_service import EmbeddingService
        embedding_service = EmbeddingService()

        # Compute embedding using the real model
        return embedding_service.embed_text(text)

    def run_ingestion_pipeline(self, directory_path: str = None) -> Dict[str, Any]:
        """
        Run the complete ingestion pipeline: scan, process, store, and index.

        Args:
            directory_path: Path to scan (defaults to configured source directory)

        Returns:
            Dictionary with ingestion results
        """
        if directory_path is None:
            directory_path = settings.source_directory

        # Scan for documents
        file_paths = self.scan_documents_directory(directory_path)
        logger.info(f"Found {len(file_paths)} files to process")

        if not file_paths:
            return {
                "processed_documents": 0,
                "created_chunks": 0,
                "skipped_documents": 0,
                "errors": []
            }

        # Create progress bar
        results = {
            "processed_documents": 0,
            "created_chunks": 0,
            "skipped_documents": 0,
            "errors": []
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing documents...", total=len(file_paths))

            for file_path in file_paths:
                try:
                    # Process document
                    document, chunks = self.process_document(file_path)

                    # Update counts
                    results["processed_documents"] += 1
                    results["created_chunks"] += len(chunks)

                    # Update progress
                    progress.update(task, advance=1, description=f"Processing: {Path(file_path).name}")

                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    progress.update(task, advance=1, description=f"Error: {Path(file_path).name}")

        return results

    def run_incremental_ingestion(self, directory_path: str = None) -> Dict[str, Any]:
        """
        Run incremental ingestion that skips unchanged documents.

        Args:
            directory_path: Path to scan (defaults to configured source directory)

        Returns:
            Dictionary with ingestion results
        """
        if directory_path is None:
            directory_path = settings.source_directory

        # Scan for documents
        file_paths = self.scan_documents_directory(directory_path)
        logger.info(f"Found {len(file_paths)} files to process")

        if not file_paths:
            return {
                "processed_documents": 0,
                "created_chunks": 0,
                "skipped_documents": 0,
                "errors": []
            }

        # Track results
        results = {
            "processed_documents": 0,
            "created_chunks": 0,
            "skipped_documents": 0,
            "errors": []
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing documents...", total=len(file_paths))

            for file_path in file_paths:
                try:
                    # Read file content to calculate checksum
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    checksum = calculate_sha256(content)

                    # Check if document with same checksum already exists
                    existing_doc = self.document_repo.find_by_checksum(checksum)
                    if existing_doc:
                        logger.info(f"Document with checksum {checksum} already exists, skipping: {file_path}")
                        results["skipped_documents"] += 1
                        progress.update(task, advance=1, description=f"Skipped: {Path(file_path).name}")
                        continue

                    # Process document since it's new or changed
                    document, chunks = self.process_document(file_path)

                    # Update counts
                    results["processed_documents"] += 1
                    results["created_chunks"] += len(chunks)

                    # Update progress
                    progress.update(task, advance=1, description=f"Processing: {Path(file_path).name}")

                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    progress.update(task, advance=1, description=f"Error: {Path(file_path).name}")

        return results