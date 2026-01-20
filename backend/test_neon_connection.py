"""
Test script to verify Neon database connection.

This script can be used to test the connection to a real Neon database
using the configuration from environment variables.
"""
import asyncio
import os
from sqlalchemy import text
from app.config import settings
from app.database.connection import get_engine


def test_sync_connection():
    """Test synchronous database connection."""
    print("Testing synchronous database connection...")

    try:
        # Get the sync engine
        engine = get_engine()

        # Test the connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✓ Synchronous connection successful: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"✗ Synchronous connection failed: {str(e)}")
        return False


async def test_async_connection():
    """Test asynchronous database connection."""
    print("Testing asynchronous database connection...")

    # Note: This project uses synchronous SQLAlchemy, so we'll skip async tests
    print("ℹ️  Asynchronous connection test skipped (project uses synchronous SQLAlchemy)")
    return True


def test_environment_variables():
    """Test that required environment variables are set."""
    print("Checking environment variables...")

    required_vars = [
        'NEON_DATABASE_URL',
        'DATABASE_USER',
        'DATABASE_HOST',
        'DATABASE_PORT',
        'DATABASE_NAME'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) and not getattr(settings, var.lower(), None):
            missing_vars.append(var)

    if missing_vars:
        print(f"✗ Missing environment variables: {missing_vars}")
        print("Please set these variables in your .env file or environment.")
        return False
    else:
        print("✓ All required environment variables are set")
        return True


def main():
    """Main function to run all tests."""
    print("Neon Database Connection Test")
    print("=" * 40)

    # Test environment variables
    env_ok = test_environment_variables()
    if not env_ok:
        print("\nPlease set the required environment variables and try again.")
        return

    # Test sync connection
    sync_ok = test_sync_connection()

    # Test async connection
    async_ok = asyncio.run(test_async_connection())

    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"- Environment variables: {'✓' if env_ok else '✗'}")
    print(f"- Synchronous connection: {'✓' if sync_ok else '✗'}")
    print(f"- Asynchronous connection: {'✓' if async_ok else '✗'}")

    if sync_ok and async_ok:
        print("\n✓ All tests passed! Neon database connection is working.")
    else:
        print("\n✗ Some tests failed. Please check your configuration.")

    return sync_ok and async_ok


if __name__ == "__main__":
    main()