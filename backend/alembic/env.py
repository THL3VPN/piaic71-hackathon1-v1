import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load manually
    import pathlib
    from dotenv.main import _walk_to_root, load_dotenv as _load_dotenv
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(dotenv_path):
        _load_dotenv(dotenv_path)

# Add the app directory to the path so we can import our models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from environment variable if available
neon_database_url = os.getenv('NEON_DATABASE_URL')
if neon_database_url:
    config.set_main_option('sqlalchemy.url', neon_database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Import models inside the functions to avoid triggering database connection on import
target_metadata = None

def get_metadata():
    from app.database.connection import Base
    from app.models.document import Document
    from app.models.chunk import Chunk
    from app.models.chat_session import ChatSession
    from app.models.chat_message import ChatMessage
    from app.models.ingestion_job import IngestionJob
    return Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if url:
        # Use the configured URL if available
        context.configure(
            url=url,
            target_metadata=get_metadata(),
            dialect_opts={"paramstyle": "named"},
        )
    else:
        # For offline operations without URL, specify dialect
        context.configure(
            target_metadata=get_metadata(),
            dialect_name="postgresql",  # Specify PostgreSQL dialect for Neon
            dialect_opts={"paramstyle": "named"},
        )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=get_metadata()
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine whether to run in offline or online mode
# Check if we're in offline mode explicitly or if no URL is configured
offline_mode = context.is_offline_mode()
url = config.get_main_option("sqlalchemy.url")

if offline_mode or not url:
    run_migrations_offline()
else:
    run_migrations_online()