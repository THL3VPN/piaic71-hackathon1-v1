#!/usr/bin/env python3
"""
Test script to verify the embedding service is working correctly.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.services.embedding_service import EmbeddingService

def test_embedding_service():
    print("Testing embedding service...")

    try:
        embedding_service = EmbeddingService()
        print("✓ Embedding service initialized successfully")

        # Test embedding a simple text
        test_text = "This is a test sentence."
        embedding = embedding_service.embed_text(test_text)

        print(f"✓ Text embedded successfully")
        print(f"  Original text: '{test_text}'")
        print(f"  Embedding length: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Last 5 values: {embedding[-5:]}")

        # Verify it matches our expected vector size
        expected_size = 384  # Size of all-MiniLM-L6-v2 embeddings
        if len(embedding) == expected_size:
            print(f"✓ Embedding size matches expected size ({expected_size})")
        else:
            print(f"✗ Embedding size mismatch: expected {expected_size}, got {len(embedding)}")

    except Exception as e:
        print(f"✗ Error testing embedding service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embedding_service()