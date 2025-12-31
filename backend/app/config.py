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

    # GitHub Pages origin for CORS
    github_pages_origin: str = "https://your-username.github.io"

    # Logging configuration
    log_level: str = "INFO"

    # Timeout configurations (in milliseconds)
    startup_timeout: int = 10000
    request_timeout: int = 30000

    # Root path (for deployment scenarios)
    root_path: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


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


# Validate settings on import
validate_settings()