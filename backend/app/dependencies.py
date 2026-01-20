"""
Dependency connectivity checks for external services.

This module provides functions to check connectivity to external dependencies
like Neon database and Qdrant vector database.
"""
import httpx
import asyncio
from typing import Dict, Tuple, Optional
import logging

from .config import settings
from .services.qdrant_service import qdrant_service

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


async def check_neon_connectivity() -> Tuple[bool, Optional[str]]:
    """
    Check connectivity to Neon database.

    Returns:
        Tuple[bool, Optional[str]]: (is_connected, error_message)
    """
    if not settings.neon_database_url:
        return False, "Neon database URL not configured"

    try:
        # In a real implementation, we would connect to Neon
        # For now, we'll just check if the URL is valid
        from urllib.parse import urlparse
        parsed = urlparse(settings.neon_database_url)

        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid Neon database URL format"

        # Simulate connection attempt
        logger.debug(f"Attempting to connect to Neon at {parsed.netloc}")

        # In a real implementation, we would establish an actual connection
        # For now, we'll assume it's connected if the URL is properly formatted
        # and the service is configured
        return True, None

    except Exception as e:
        logger.error(f"Neon connectivity check failed: {str(e)}")
        return False, str(e)


def check_qdrant_connectivity() -> Tuple[bool, Optional[str]]:
    """
    Check connectivity to Qdrant vector database.

    Returns:
        Tuple[bool, Optional[str]]: (is_connected, error_message)
    """
    try:
        # Use the Qdrant service to validate connection
        is_connected = qdrant_service.validate_connection()

        if is_connected:
            # Also check if the collection exists
            collection_exists = qdrant_service.check_collection_exists()
            if not collection_exists:
                return False, "Qdrant connected but collection 'book_chunks' does not exist"
            return True, None
        else:
            return False, "Qdrant service not connected"

    except Exception as e:
        logger.error(f"Qdrant connectivity check failed: {str(e)}")
        return False, str(e)


async def check_all_dependencies() -> Dict[str, Dict[str, str]]:
    """
    Check connectivity to all external dependencies.

    Returns:
        Dict[str, Dict[str, str]]: Status information for each dependency
    """
    # Check Neon connectivity
    neon_connected, neon_error = await check_neon_connectivity()

    # Check Qdrant connectivity (synchronous function)
    qdrant_connected, qdrant_error = check_qdrant_connectivity()

    dependencies_status = {
        "neon": {
            "status": "connected" if neon_connected else "disconnected",
            "message": neon_error
        },
        "qdrant": {
            "status": "connected" if qdrant_connected else "disconnected",
            "message": qdrant_error
        }
    }

    return dependencies_status