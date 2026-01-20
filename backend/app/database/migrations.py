"""
Database migration utilities for the backend service.

This module provides functions for managing database migrations
using Alembic, including migration execution and rollback capabilities.
"""
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from typing import Optional
import os
from pathlib import Path


def get_alembic_config(database_url: Optional[str] = None) -> Config:
    """
    Get Alembic configuration for database migrations.

    Args:
        database_url: Optional database URL to override default

    Returns:
        Config: Alembic configuration object
    """
    # Create alembic configuration
    alembic_cfg = Config()

    # Set the script location - this assumes migrations are in backend/migrations
    migrations_path = Path(__file__).parent.parent / "migrations"
    alembic_cfg.set_main_option("script_location", str(migrations_path))

    # Set the database URL if provided
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    return alembic_cfg


def run_migrations_online(database_url: Optional[str] = None, revision: str = "head"):
    """
    Run database migrations online against the configured database.

    Args:
        database_url: Optional database URL to override default
        revision: Migration revision to upgrade to (default: "head")
    """
    alembic_cfg = get_alembic_config(database_url)
    command.upgrade(alembic_cfg, revision)


def run_migrations_offline(database_url: Optional[str] = None):
    """
    Generate migration scripts without applying them to the database.

    Args:
        database_url: Optional database URL to override default
    """
    alembic_cfg = get_alembic_config(database_url)
    command.revision(alembic_cfg, autogenerate=True, message="Auto-generated migration")


def check_current_revision(database_url: Optional[str] = None):
    """
    Check the current migration revision of the database.

    Args:
        database_url: Optional database URL to override default
    """
    alembic_cfg = get_alembic_config(database_url)
    command.current(alembic_cfg)


def run_downgrade(database_url: Optional[str] = None, revision: str = "-1"):
    """
    Rollback database migrations.

    Args:
        database_url: Optional database URL to override default
        revision: Migration revision to downgrade to (default: "-1" for one step back)
    """
    alembic_cfg = get_alembic_config(database_url)
    command.downgrade(alembic_cfg, revision)


def create_migration(database_url: Optional[str] = None, message: str = "New migration"):
    """
    Create a new migration file with auto-generated changes.

    Args:
        database_url: Optional database URL to override default
        message: Migration message/description
    """
    alembic_cfg = get_alembic_config(database_url)
    command.revision(alembic_cfg, autogenerate=True, message=message)