#!/usr/bin/env python3
"""
Script to check the database state.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.database.connection import get_db
from app.database.document_repository import DocumentRepository
from app.database.chunk_repository import ChunkRepository

def check_database_state():
    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        doc_repo = DocumentRepository(db)
        chunk_repo = ChunkRepository(db)

        # Count documents
        all_docs = doc_repo.get_all()
        print(f"Total documents in DB: {len(all_docs)}")

        # Count chunks
        all_chunks = chunk_repo.get_all()
        print(f"Total chunks in DB: {len(all_chunks)}")

        if all_docs:
            print("\nFirst few documents:")
            for doc in all_docs[:5]:
                print(f"  ID: {doc.id}, Title: {doc.title}, Source: {doc.source_path}")

        if all_chunks:
            print(f"\nFirst few chunks:")
            for chunk in all_chunks[:5]:
                print(f"  ID: {chunk.id}, Doc ID: {chunk.document_id}, Index: {chunk.chunk_index}, Length: {len(chunk.chunk_text)}")

    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    check_database_state()