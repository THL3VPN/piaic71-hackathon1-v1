"""
Citation service for the RAG system.
"""
from typing import List
from app.models.chunk import Chunk


class CitationService:
    """
    Service class for handling citation formatting and generation.
    """

    def format_citation(self, source_path: str, heading: str, chunk_index: int) -> str:
        """
        Format a citation string with source path, heading, and chunk index.

        Args:
            source_path: Path to the source document
            heading: Heading where the content appears
            chunk_index: Index of the chunk in the document

        Returns:
            Formatted citation string
        """
        return f"[Source: {source_path}, Heading: {heading}, Chunk: {chunk_index}]"

    def build_context_with_citations(self, chunks: List[Chunk]) -> tuple[str, List[str]]:
        """
        Build context from chunks with proper citations.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Tuple of (formatted context string, list of citations)
        """
        context_parts = []
        citations = []

        for chunk in chunks:
            # Get metadata from chunk
            metadata = chunk.chunk_metadata or {}
            source_path = metadata.get('source_path', 'unknown')
            heading = metadata.get('heading', 'unknown')
            chunk_index = metadata.get('chunk_index', -1)

            # Add chunk content to context
            context_parts.append(chunk.chunk_text)

            # Create citation for this chunk
            citation = self.format_citation(source_path, heading, chunk_index)
            citations.append(citation)

        context = "\n\n".join(context_parts)
        return context, citations

    def format_chunk_with_citation(self, chunk: Chunk) -> str:
        """
        Format a single chunk with its citation.

        Args:
            chunk: The chunk to format

        Returns:
            Formatted string with content and citation
        """
        metadata = chunk.chunk_metadata or {}
        source_path = metadata.get('source_path', 'unknown')
        heading = metadata.get('heading', 'unknown')
        chunk_index = metadata.get('chunk_index', -1)

        citation = self.format_citation(source_path, heading, chunk_index)
        return f"{chunk.chunk_text}\n{citation}"