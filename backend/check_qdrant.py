#!/usr/bin/env python3
"""
Script to check the Qdrant vector store state.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.services.qdrant_service import qdrant_service
from qdrant_client.http import models

def check_qdrant_state():
    try:
        collection_name = "documents"  # This is the default from config

        # Get collection info using the low-level client
        collection_info = qdrant_service.client.get_collection(collection_name)

        print(f"Collection '{collection_name}' info:")
        print(f"  Status: {collection_info.status}")
        print(f"  Points count: {collection_info.points_count}")

        # Check vector configuration
        if hasattr(collection_info.config.params, 'vectors'):
            vector_config = collection_info.config.params.vectors
            if isinstance(vector_config, dict):
                # Multiple vector configuration
                for vec_name, vec_params in vector_config.items():
                    print(f"  Vector '{vec_name}' size: {vec_params.size}")
                    print(f"  Vector '{vec_name}' distance: {vec_params.distance}")
            else:
                # Single vector configuration
                print(f"  Vector size: {vector_config.size}")
                print(f"  Distance: {vector_config.distance}")
        else:
            print(f"  Vector params: {collection_info.config.params}")

        # Get some sample points to verify they exist
        if collection_info.points_count > 0:
            # Scroll to get some points
            scroll_result = qdrant_service.client.scroll(
                collection_name=collection_name,
                limit=5,
                with_payload=True,
                with_vectors=False
            )

            print(f"\nFirst 5 points in collection:")
            for idx, (point, _) in enumerate(zip(scroll_result[0], range(5))):
                print(f"  Point {idx}: ID={point.id}, Payload keys={list(point.payload.keys())}")
                if 'title' in point.payload:
                    print(f"    Title: {point.payload['title']}")
                if 'content' in point.payload:
                    print(f"    Content preview: {point.payload['content'][:100]}...")

    except Exception as e:
        print(f"Error checking Qdrant: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_qdrant_state()