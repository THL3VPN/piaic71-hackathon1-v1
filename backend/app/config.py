"""
Configuration module for backend service.

This module defines the application settings using Pydantic BaseSettings,
validating environment variables at startup and providing configuration
for the service components.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Backend configuration
    backend_host: str = "localhost"
    backend_port: int = 8000

    # Database connections
    neon_database_url: Optional[str] = None
    qdrant_url: Optional[str] = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None

    # Qdrant vector configuration
    vector_size: int = 384  # Changed to match all-MiniLM-L6-v2 model output
    distance_metric: str = "Cosine"

    # GitHub Pages origin for CORS
    github_pages_origin: str = "https://your-username.github.io"

    # Logging configuration
    log_level: str = "INFO"

    # Timeout configurations (in milliseconds)
    startup_timeout: int = 10000
    request_timeout: int = 30000

    # Root path (for deployment scenarios)
    root_path: str = ""

    # Ingestion configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_document_size: int = 10 * 1024 * 1024  # 10MB
    supported_extensions: List[str] = [".md", ".mdx"]
    source_directory: str = "/home/aie/all_data/piaic71-hackathon1-v1/book/docs"
    progress_refresh_rate: float = 0.1  # seconds

    # RAG Retrieval configuration
    top_k: int = 5
    similarity_threshold: float = 0.1
    max_context_length: int = 3000
    chunk_size_limit: int = 1000
    chunk_overlap_default: int = 200
    qdrant_collection_name: str = "documents"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra environment variables not defined in this class


# Create global settings instance
settings = Settings()


def validate_settings():
    """
    Validate settings at startup.

    Raises ValueError if any required settings are invalid.
    """
    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if settings.log_level.upper() not in valid_log_levels:
        raise ValueError(f"Invalid log level: {settings.log_level}. Must be one of {valid_log_levels}")

    # Validate port range
    if not (1 <= settings.backend_port <= 65535):
        raise ValueError(f"Invalid port: {settings.backend_port}. Must be between 1 and 65535")

    # Validate timeout values
    if settings.startup_timeout <= 0:
        raise ValueError(f"Startup timeout must be positive, got {settings.startup_timeout}")

    if settings.request_timeout <= 0:
        raise ValueError(f"Request timeout must be positive, got {settings.request_timeout}")

    # Validate Qdrant port range
    if not (1 <= settings.qdrant_port <= 65535):
        raise ValueError(f"Invalid Qdrant port: {settings.qdrant_port}. Must be between 1 and 65535")

    # Validate vector size
    if settings.vector_size <= 0:
        raise ValueError(f"Vector size must be positive, got {settings.vector_size}")

    # Validate distance metric
    valid_distance_metrics = ["Cosine", "Euclidean", "Dot"]
    if settings.distance_metric not in valid_distance_metrics:
        raise ValueError(f"Invalid distance metric: {settings.distance_metric}. Must be one of {valid_distance_metrics}")

    # Validate ingestion settings
    if settings.chunk_size <= 0:
        raise ValueError(f"Chunk size must be positive, got {settings.chunk_size}")

    if settings.chunk_overlap < 0:
        raise ValueError(f"Chunk overlap cannot be negative, got {settings.chunk_overlap}")

    if settings.max_document_size <= 0:
        raise ValueError(f"Max document size must be positive, got {settings.max_document_size}")

    if not settings.supported_extensions:
        raise ValueError("At least one supported extension must be specified")

    if not settings.source_directory:
        raise ValueError("Source directory must be specified")

    # Validate RAG parameters
    if settings.top_k <= 0:
        raise ValueError(f"Top K must be positive, got {settings.top_k}")

    if not (0.0 <= settings.similarity_threshold <= 1.0):
        raise ValueError(f"Similarity threshold must be between 0.0 and 1.0, got {settings.similarity_threshold}")

    if settings.max_context_length <= 0:
        raise ValueError(f"Max context length must be positive, got {settings.max_context_length}")

    if settings.vector_size <= 0:
        raise ValueError(f"Vector size must be positive, got {settings.vector_size}")

    if settings.chunk_size_limit <= 0:
        raise ValueError(f"Chunk size limit must be positive, got {settings.chunk_size_limit}")

    if settings.chunk_overlap_default < 0:
        raise ValueError(f"Chunk overlap cannot be negative, got {settings.chunk_overlap_default}")


# Validate settings on import
validate_settings()