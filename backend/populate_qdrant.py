#!/usr/bin/env python3
"""
Script to populate Qdrant from vectors stored in the database.
"""
import sys
import json
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.database.connection import get_db
from app.database.chunk_repository import ChunkRepository
from app.services.qdrant_service import qdrant_service
from app.models.document import Document
from sqlalchemy.orm import joinedload

def populate_qdrant_from_db():
    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        chunk_repo = ChunkRepository(db)

        # Get all chunks that have vectors
        all_chunks = chunk_repo.get_all()
        chunks_with_vectors = [chunk for chunk in all_chunks if chunk.vector]

        print(f"Found {len(chunks_with_vectors)} chunks with vectors in database")

        if not chunks_with_vectors:
            print("No chunks with vectors found in database")
            return

        # Get document mapping to access titles and source paths
        document_ids = list(set(chunk.document_id for chunk in chunks_with_vectors))
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        doc_map = {str(doc.id): doc for doc in documents}

        # Populate Qdrant
        success_count = 0
        error_count = 0

        for chunk in chunks_with_vectors:
            try:
                # Deserialize the vector from JSON string
                vector = json.loads(chunk.vector)

                # Get document info
                doc = doc_map.get(str(chunk.document_id))
                title = doc.title if doc else ""
                source_path = doc.source_path if doc else ""

                # Create payload
                payload = {
                    'document_id': str(chunk.document_id),
                    'source_path': source_path,
                    'title': title,
                    'chunk_index': chunk.chunk_index,
                    'content': chunk.chunk_text
                }

                # Upsert to Qdrant
                qdrant_service.upsert_point(
                    chunk_id=str(chunk.id),
                    vector=vector,
                    payload=payload
                )

                success_count += 1
                if success_count % 10 == 0:
                    print(f"Progress: {success_count}/{len(chunks_with_vectors)} chunks processed")

            except Exception as e:
                print(f"Error upserting chunk {chunk.id} to Qdrant: {e}")
                error_count += 1

        print(f"Completed! Successfully upserted {success_count} chunks to Qdrant, {error_count} errors")

        # Verify by checking Qdrant collection
        collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
        print(f"Qdrant collection now has {collection_info.points_count} points")

    except Exception as e:
        print(f"Error populating Qdrant: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    populate_qdrant_from_db()