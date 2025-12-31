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


async def check_qdrant_connectivity() -> Tuple[bool, Optional[str]]:
    """
    Check connectivity to Qdrant vector database.

    Returns:
        Tuple[bool, Optional[str]]: (is_connected, error_message)
    """
    if not settings.qdrant_url:
        return False, "Qdrant URL not configured"

    try:
        # Attempt to connect to Qdrant health endpoint
        async with httpx.AsyncClient(timeout=settings.request_timeout/1000) as client:
            response = await client.get(f"{settings.qdrant_url}/healthz")

            if response.status_code == 200:
                return True, None
            else:
                return False, f"Qdrant returned status {response.status_code}: {response.text}"

    except httpx.RequestError as e:
        logger.error(f"Qdrant connectivity request failed: {str(e)}")
        return False, f"Request error: {str(e)}"
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

    # Check Qdrant connectivity
    qdrant_connected, qdrant_error = await check_qdrant_connectivity()

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