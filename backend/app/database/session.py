"""
Database session management for the backend service.

This module provides utilities for managing database sessions,
including session creation, management, and context managers.
"""
from sqlalchemy.orm import Session
from typing import Generator
from contextlib import contextmanager
from .connection import get_session_local, get_engine


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        Session: Database session that is automatically closed after use
    """
    session = get_session_local()()
    try:
        yield session
    finally:
        session.close()


def get_session() -> Session:
    """
    Get a database session instance.

    Returns:
        Session: Database session instance
    """
    return get_session_local()()


def close_session(session: Session):
    """
    Close a database session.

    Args:
        session: Database session to close
    """
    session.close()


def execute_in_transaction(func, *args, **kwargs):
    """
    Execute a function within a database transaction.

    Args:
        func: Function to execute within transaction
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function execution
    """
    with get_db_session() as session:
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise


class DatabaseSessionManager:
    """
    Database session manager for handling session lifecycle.
    """
    def __init__(self):
        self.engine = get_engine()
        self.get_session_local = get_session_local

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            Session: New database session instance
        """
        return self.get_session_local()()

    def close_session(self, session: Session):
        """
        Close a database session.

        Args:
            session: Database session to close
        """
        session.close()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Yields:
            Session: Database session that is automatically closed after use
        """
        session = self.get_session_local()()
        try:
            yield session
        finally:
            session.close()