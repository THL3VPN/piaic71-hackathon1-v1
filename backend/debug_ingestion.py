#!/usr/bin/env python3
"""
Debug script to test the full ingestion process step by step.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.database.connection import get_db
from app.services.ingestion_service import IngestionService
from app.utils.text_extractor import extract_text_with_frontmatter
from app.utils.chunker import chunk_document

def test_full_ingestion_step_by_step():
    print(f"Source directory: {settings.source_directory}")

    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Create ingestion service
        ingestion_service = IngestionService(db)

        # Test with a single document
        sample_doc_path = "/home/aie/all_data/piaic71-hackathon1-v1/book/docs/intro.md"

        print(f"Processing document: {sample_doc_path}")

        # Read file content (this is what process_document does)
        with open(sample_doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"File content length: {len(content)}")

        # Calculate checksum
        from app.utils.checksum import calculate_sha256
        checksum = calculate_sha256(content)
        print(f"Checksum: {checksum[:16]}...")

        # Check if document with same checksum already exists
        existing_doc = ingestion_service.document_repo.find_by_checksum(checksum)
        if existing_doc:
            print(f"Document already exists with ID: {existing_doc.id}")
            return

        # Extract text and metadata
        clean_content, frontmatter, title = extract_text_with_frontmatter(content)
        print(f"Clean content length: {len(clean_content)}")
        print(f"Title: {title}")

        # Create or update document in database
        relative_path = str(Path(sample_doc_path).relative_to(settings.source_directory))
        print(f"Relative path: {relative_path}")

        document = ingestion_service.document_repo.create(
            source_path=relative_path,
            title=title,
            checksum=checksum,
            content=clean_content
        )
        print(f"Created document with ID: {document.id}")

        # Chunk the document
        chunks = chunk_document(clean_content, str(document.id))
        print(f"Number of chunks from chunker: {len(chunks)}")

        # Process and store chunks
        chunk_models = []
        for idx, chunk in enumerate(chunks):
            print(f"Processing chunk {idx}: length={len(chunk.content)}, id={chunk.id[:16]}...")

            # Create chunk in database
            chunk_model = ingestion_service.chunk_repo.create(
                document_id=document.id,
                chunk_index=chunk.index,
                chunk_text=chunk.content,
                chunk_hash=chunk.id,
                metadata=None
            )
            print(f"Created chunk model with ID: {chunk_model.id}")
            chunk_models.append(chunk_model)

            # Test embedding calculation
            try:
                embedding = ingestion_service.compute_embedding(chunk.content)
                print(f"Computed embedding of length: {len(embedding)}")

                # Test Qdrant upsert
                from app.services.qdrant_service import qdrant_service
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
                print(f"Successfully upserted chunk to Qdrant: {chunk.id[:16]}...")
            except Exception as e:
                print(f"Failed to upsert chunk {chunk.id} to Qdrant: {e}")

        print(f"Final result: {len(chunk_models)} chunk models created")

    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    test_full_ingestion_step_by_step()