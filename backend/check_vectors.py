#!/usr/bin/env python3
"""
Script to check if vectors were stored in the database.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.database.connection import get_db
from app.database.chunk_repository import ChunkRepository

def check_vectors_in_db():
    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        chunk_repo = ChunkRepository(db)

        # Get first few chunks to check if vectors are stored
        all_chunks = chunk_repo.get_all()
        print(f"Total chunks in DB: {len(all_chunks)}")

        if all_chunks:
            print("\nChecking first few chunks for vector data:")
            for i, chunk in enumerate(all_chunks[:3]):
                print(f"  Chunk {i}: ID={chunk.id}, Doc ID={chunk.document_id}")
                print(f"    Text preview: {chunk.chunk_text[:100]}...")
                print(f"    Has vector data: {chunk.vector is not None}")
                if chunk.vector:
                    print(f"    Vector length: {len(chunk.vector) if hasattr(chunk.vector, '__len__') else 'N/A'}")
                print(f"    Chunk index: {chunk.chunk_index}")
                print(f"    Chunk hash: {chunk.chunk_hash[:16]}...")

    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    check_vectors_in_db()