"""
Configuration for ingestion parameters.
"""
from typing import Optional
from pydantic import BaseModel


class IngestionConfig(BaseModel):
    """
    Configuration for document ingestion parameters.
    """
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_document_size: int = 10 * 1024 * 1024  # 10MB
    supported_extensions: list[str] = [".md", ".mdx"]
    source_directory: str = "../book/docs"
    progress_refresh_rate: float = 0.1  # seconds