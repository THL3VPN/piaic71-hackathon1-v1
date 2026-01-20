"""
Database connection utilities for the backend service.

This module provides database connection management using SQLAlchemy,
including engine creation, session management, and connection utilities.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from .config import db_settings

# Create a Base class for declarative models
Base = declarative_base()

# Global variables for engine and session - initialized lazily
_engine = None
_SessionLocal = None


def get_engine():
    """
    Get or create the database engine instance.

    Returns:
        Engine: SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        database_url = db_settings.get_database_url()
        _engine = create_engine(
            database_url,
            pool_size=db_settings.database_pool_size,
            pool_timeout=db_settings.database_pool_timeout,
            pool_recycle=db_settings.database_pool_recycle,
            echo=db_settings.sqlalchemy_echo
        )
    return _engine


def get_session_local():
    """
    Get or create the SessionLocal class.

    Returns:
        sessionmaker: SessionLocal class for creating database sessions
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db() -> Generator:
    """
    Dependency function that provides database sessions for FastAPI endpoints.

    Yields:
        Generator: Database session that is automatically closed after use
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.

    This function should be called during application startup to ensure
    all database tables are created according to the defined models.
    """
    Base.metadata.create_all(bind=get_engine())