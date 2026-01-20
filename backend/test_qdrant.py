#!/usr/bin/env python3
"""
Test script to verify Qdrant operations are working correctly.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import EmbeddingService

def test_qdrant_operations():
    print("Testing Qdrant operations...")

    try:
        # Test if collection exists
        collection_exists = qdrant_service.check_collection_exists()
        print(f"✓ Collection exists: {collection_exists}")

        # Get initial count
        collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
        initial_points = collection_info.points_count
        print(f"✓ Initial points in collection: {initial_points}")

        # Create a test embedding
        embedding_service = EmbeddingService()
        test_text = "This is a test document about artificial intelligence and machine learning."
        embedding = embedding_service.embed_text(test_text)
        print(f"✓ Created test embedding of length: {len(embedding)}")

        # Try to upsert a point
        import uuid
        test_chunk_id = str(uuid.uuid4())

        payload = {
            'document_id': str(uuid.uuid4()),
            'source_path': 'test/test.md',
            'title': 'Test Document',
            'chunk_index': 0,
            'content': test_text
        }

        success = qdrant_service.upsert_point(
            chunk_id=test_chunk_id,
            vector=embedding,
            payload=payload
        )

        print(f"✓ Upsert operation successful: {success}")

        # Check count after upsert
        collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
        after_upsert_points = collection_info.points_count
        print(f"✓ Points in collection after upsert: {after_upsert_points}")

        # Try to search
        query_embedding = embedding_service.embed_text("artificial intelligence")
        search_results = qdrant_service.search_similar(
            query_vector=query_embedding,
            limit=5
        )

        print(f"✓ Search operation completed, found {len(search_results)} results")

        if search_results:
            print(f"  First result: ID={search_results[0]['chunk_id'][:8]}..., Score={search_results[0]['score']:.4f}")

        # Clean up - delete the test point
        try:
            qdrant_service.client.delete(
                collection_name=qdrant_service.collection_name,
                points_selector=[test_chunk_id]
            )
            print("✓ Test point cleaned up successfully")

            # Check final count
            collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
            final_points = collection_info.points_count
            print(f"✓ Final points in collection: {final_points}")

        except Exception as e:
            print(f"⚠ Could not clean up test point: {e}")

    except Exception as e:
        print(f"✗ Error testing Qdrant operations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qdrant_operations()