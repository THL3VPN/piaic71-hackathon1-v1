"""
Database configuration module for the backend service.

This module defines the database settings using Pydantic BaseSettings,
configuring connection parameters for the Neon PostgreSQL database.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class DatabaseSettings(BaseSettings):
    """
    Database settings loaded from environment variables.
    """
    # Database connection
    neon_database_url: Optional[str] = None  # For backwards compatibility with .env.example
    database_url: Optional[str] = None
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "piaic71_hackathon"
    database_user: str = "postgres"
    database_password: str = ""

    # Connection pool settings
    database_pool_size: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600

    # SQLAlchemy settings
    sqlalchemy_echo: bool = False  # Set to True for SQL query logging

    class Config:
        # Only load database-specific variables
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Use extra='ignore' to ignore non-database settings
        extra = 'ignore'

    def get_database_url(self) -> Optional[str]:
        """
        Get the database URL, prioritizing neon_database_url if available.
        """
        # If neon_database_url is provided, use it
        if self.neon_database_url:
            return self.neon_database_url
        # If database_url is provided, use it
        if self.database_url:
            return self.database_url
        # Otherwise, construct from individual components
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"


# Create global database settings instance
db_settings = DatabaseSettings()