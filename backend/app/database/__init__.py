"""
Initialization module for database components in the backend service.

This module provides imports for all database utilities to enable
easy access from other parts of the application.
"""
# Import core database components
from .connection import get_engine, get_session_local, Base, get_db, init_db
from .config import db_settings
from .session import get_db_session, DatabaseSessionManager
from .migrations import (
    run_migrations_online,
    run_migrations_offline,
    check_current_revision,
    run_downgrade,
    create_migration
)

# Define what gets imported with "from app.database import *"
__all__ = [
    # Core components
    "get_engine",
    "get_session_local",
    "Base",
    "get_db",
    "init_db",

    # Configuration
    "db_settings",

    # Session management
    "get_db_session",
    "DatabaseSessionManager",

    # Migration utilities
    "run_migrations_online",
    "run_migrations_offline",
    "check_current_revision",
    "run_downgrade",
    "create_migration"
]