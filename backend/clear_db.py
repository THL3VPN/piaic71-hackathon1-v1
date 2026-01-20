#!/usr/bin/env python3
"""
Script to clear the document and chunk databases and Qdrant collection to start fresh.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.database.connection import get_db
from app.database.document_repository import DocumentRepository
from app.database.chunk_repository import ChunkRepository
from app.services.qdrant_service import qdrant_service

def clear_all_data():
    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        doc_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)

        # Delete all chunks first (due to foreign key constraints)
        all_chunks = chunk_repo.get_all()
        print(f"Deleting {len(all_chunks)} chunks from database...")
        for chunk in all_chunks:
            db.delete(chunk)

        # Commit the chunk deletions
        db.commit()

        # Delete all documents
        all_docs = doc_repo.get_all()
        print(f"Deleting {len(all_docs)} documents from database...")
        for doc in all_docs:
            db.delete(doc)

        # Commit the document deletions
        db.commit()

        # Clear Qdrant collection
        collection_name = "documents"
        try:
            # Check if collection exists
            collection_info = qdrant_service.client.get_collection(collection_name)
            print(f"Found Qdrant collection '{collection_name}' with {collection_info.points_count} points")

            # Delete the collection
            qdrant_service.client.delete_collection(collection_name)
            print(f"Deleted Qdrant collection '{collection_name}'")
        except Exception as qdrant_error:
            print(f"Qdrant collection '{collection_name}' doesn't exist or error deleting: {qdrant_error}")

        print("All data cleared successfully!")

    except Exception as e:
        print(f"Error clearing data: {e}")
        db.rollback()
    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    clear_all_data()