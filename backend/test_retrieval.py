#!/usr/bin/env python3
"""
Test script to verify the retrieval functionality is working.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.database.connection import get_db
from app.services.retrieval_service import RetrievalService
from app.services.embedding_service import EmbeddingService

def test_retrieval():
    # Initialize database connection
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Initialize retrieval service
        retrieval_service = RetrievalService(db=db)

        # Test embedding a question
        question = "What is this book about?"
        print(f"Testing retrieval for question: '{question}'")

        # Embed the question
        query_vector = retrieval_service.embed_question(question)
        print(f"Query vector length: {len(query_vector)}")

        # Perform vector search
        search_results = retrieval_service.perform_vector_search(query_vector, top_k=5)
        print(f"Number of search results: {len(search_results)}")

        for i, result in enumerate(search_results):
            print(f"Result {i+1}: ID={result['id'][:12]}..., Score={result['score']:.4f}")

        # Try to retrieve chunks by IDs if there are results
        if search_results:
            chunk_ids = [result['id'] for result in search_results]
            chunks = retrieval_service.fetch_chunks_by_ids(chunk_ids)
            print(f"Fetched {len(chunks)} chunks from database")

            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: Doc ID={chunk.document_id}, Length={len(chunk.chunk_text)}")
                print(f"  Preview: {chunk.chunk_text[:100]}...")
        else:
            print("No results found from vector search")

        # Test the full retrieval pipeline
        ranked_chunks = retrieval_service.retrieve_and_rank_chunks(
            question=question,
            top_k=5,
            similarity_threshold=0.0  # Lower threshold to see if there are any results
        )
        print(f"Ranked chunks with low threshold: {len(ranked_chunks)}")

    except Exception as e:
        print(f"Error during retrieval test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    test_retrieval()