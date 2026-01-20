#!/usr/bin/env python3
"""
Debug script to test the chunking functionality.
"""
import sys
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent))

from app.utils.chunker import chunk_document
from app.config import settings
from app.utils.text_extractor import extract_text_with_frontmatter

def test_chunking():
    print(f"Configured chunk size: {settings.chunk_size}")
    print(f"Configured chunk overlap: {settings.chunk_overlap}")

    # Read a sample document
    sample_doc_path = "/home/aie/all_data/piaic71-hackathon1-v1/book/docs/intro.md"

    with open(sample_doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Sample document content length: {len(content)}")
    print(f"Sample content preview: {content[:200]}...")

    # Extract text with frontmatter
    clean_content, frontmatter, title = extract_text_with_frontmatter(content)
    print(f"Clean content length: {len(clean_content)}")
    print(f"Frontmatter: {frontmatter}")
    print(f"Title: {title}")

    # Test chunking
    chunks = chunk_document(clean_content, "test_doc_123")
    print(f"Number of chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"Chunk {i} length: {len(chunk.content)}, content preview: {chunk.content[:100]}...")

    if not chunks:
        print("No chunks were created! This explains the 'Chunks created: 0' issue.")

        # Let's try with a simpler test
        test_content = "This is a test document with enough content to create at least one chunk. " * 10
        test_chunks = chunk_document(test_content, "test_doc_456")
        print(f"Test content length: {len(test_content)}")
        print(f"Test chunks created: {len(test_chunks)}")
        if test_chunks:
            print(f"Test chunk 0 length: {len(test_chunks[0].content)}")

if __name__ == "__main__":
    test_chunking()