"""
Document chunking utilities for creating deterministic chunks.
"""
import hashlib
import uuid
from typing import List, Dict, Any
from dataclasses import dataclass
from app.config import settings


@dataclass
class Chunk:
    """Represents a document chunk."""
    content: str
    index: int
    id: str


class DocumentChunker:
    """Handles document chunking with deterministic IDs."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the chunker with configuration.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk_document(self, content: str, doc_id: str = None) -> List[Chunk]:
        """
        Split document content into chunks with deterministic IDs.

        Args:
            content: Document content to chunk
            doc_id: Optional document ID to include in chunk ID generation

        Returns:
            List of Chunk objects
        """
        if not content:
            return []

        chunks = []
        start_idx = 0
        chunk_idx = 0

        while start_idx < len(content):
            # Determine the end position for this chunk
            end_idx = start_idx + self.chunk_size

            # If this is not the last chunk, try to break at a sentence or word boundary
            if end_idx < len(content):
                # Look for a good breaking point near the end
                search_start = end_idx - 50  # Look back up to 50 characters
                search_start = max(search_start, start_idx)

                # First, try to break at sentence endings
                sentence_break = -1
                for i in range(min(end_idx, len(content)) - 1, search_start, -1):
                    if content[i] in '.!?':
                        sentence_break = i + 1
                        break

                # If no sentence break found, try word boundaries
                if sentence_break == -1:
                    for i in range(min(end_idx, len(content)) - 1, search_start, -1):
                        if content[i] in ' \t\n':
                            sentence_break = i + 1
                            break

                # Use the best breaking point found, or the full chunk size
                if sentence_break != -1 and sentence_break > start_idx:
                    end_idx = sentence_break
                else:
                    # If we couldn't find a good breaking point, just use the full chunk size
                    end_idx = min(end_idx, len(content))

            # Extract the chunk content
            chunk_content = content[start_idx:end_idx]

            # Generate a deterministic ID based on the content and document ID
            chunk_id = self._generate_chunk_id(chunk_content, doc_id, chunk_idx)

            # Create the chunk
            chunk = Chunk(
                content=chunk_content,
                index=chunk_idx,
                id=chunk_id
            )

            chunks.append(chunk)

            # Move to the next chunk position
            # If there's overlap, start from the overlap position
            next_start = end_idx - self.chunk_overlap
            start_idx = max(next_start, end_idx)  # Ensure we make progress
            chunk_idx += 1

        return chunks

    def _generate_chunk_id(self, content: str, doc_id: str, chunk_index: int) -> str:
        """
        Generate a deterministic ID for a chunk based on its content and position.

        Args:
            content: Chunk content
            doc_id: Document ID
            chunk_index: Position of chunk in document

        Returns:
            Deterministic chunk ID as a proper UUID string
        """
        # Create a unique identifier based on document ID, content, and position
        identifier = f"{doc_id}:{chunk_index}:{content[:100]}"  # Use first 100 chars for efficiency
        # Create a deterministic UUID from the hash
        sha_hash = hashlib.sha256(identifier.encode()).digest()
        # Use the first 16 bytes to create a UUID
        return str(uuid.UUID(bytes=sha_hash[:16]))


def chunk_document(content: str, doc_id: str = None, chunk_size: int = None, chunk_overlap: int = None) -> List[Chunk]:
    """
    Convenience function to chunk a document.

    Args:
        content: Document content to chunk
        doc_id: Optional document ID to include in chunk ID generation
        chunk_size: Override default chunk size
        chunk_overlap: Override default chunk overlap

    Returns:
        List of Chunk objects
    """
    chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.chunk_document(content, doc_id)