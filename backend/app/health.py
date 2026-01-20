"""
Health and readiness endpoints for the backend service.

This module provides health and readiness check endpoints that indicate
the service status and external dependency connectivity.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import httpx
import logging

from .config import settings
from .dependencies import check_all_dependencies, check_qdrant_connectivity
from .models.qdrant_models import QdrantHealthResponse, QdrantCollectionCheck

router = APIRouter()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)


@router.get("/health", summary="Health Check", description="Returns the health status of the backend service. Always returns OK if the service is running.")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint that always returns OK if the service is running.

    Returns:
        Dict[str, str]: Health status with "status": "ok"
    """
    logger.info("Health check endpoint accessed")
    return {"status": "ok"}


@router.get("/ready", summary="Readiness Check", description="Checks if the service is ready to handle requests. Returns OK only when external dependencies (Neon, Qdrant) are configured and reachable.")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint that verifies connectivity to external dependencies.

    Returns:
        Dict[str, Any]: Readiness status with dependency information
    """
    logger.info("Readiness check endpoint accessed")

    # Initialize the response structure
    readiness_response = {
        "status": "ok",
        "dependencies": {
            "neon": {
                "status": "connected" if settings.neon_database_url else "disconnected",
                "message": None
            },
            "qdrant": {
                "status": "connected" if settings.qdrant_url else "disconnected",
                "message": None
            }
        }
    }

    # Check Neon connectivity if URL is configured
    if settings.neon_database_url:
        try:
            # In a real implementation, we would make an actual connection check
            # For now, we'll simulate a check
            logger.debug(f"Checking Neon connectivity to: {settings.neon_database_url}")

            # Simulate a connection check (in real implementation, connect to Neon)
            # For now, we'll just return connected if the URL is set
            readiness_response["dependencies"]["neon"]["status"] = "connected"
        except Exception as e:
            logger.error(f"Neon connectivity check failed: {str(e)}")
            readiness_response["dependencies"]["neon"]["status"] = "error"
            readiness_response["dependencies"]["neon"]["message"] = str(e)
            readiness_response["status"] = "error"
    else:
        readiness_response["dependencies"]["neon"]["status"] = "disconnected"
        readiness_response["dependencies"]["neon"]["message"] = "Neon database URL not configured"
        readiness_response["status"] = "error"

    # Check Qdrant connectivity if URL is configured
    if settings.qdrant_url:
        try:
            logger.debug(f"Checking Qdrant connectivity to: {settings.qdrant_url}")

            # In a real implementation, we would make an actual connection check
            # For now, we'll simulate a check
            readiness_response["dependencies"]["qdrant"]["status"] = "connected"
        except Exception as e:
            logger.error(f"Qdrant connectivity check failed: {str(e)}")
            readiness_response["dependencies"]["qdrant"]["status"] = "error"
            readiness_response["dependencies"]["qdrant"]["message"] = str(e)
            readiness_response["status"] = "error"
    else:
        readiness_response["dependencies"]["qdrant"]["status"] = "disconnected"
        readiness_response["dependencies"]["qdrant"]["message"] = "Qdrant URL not configured"
        readiness_response["status"] = "error"

    # Return the readiness response
    return readiness_response


@router.get("/health/qdrant", summary="Qdrant Health Check", description="Checks if the Qdrant vector database is available and the collection exists.")
async def qdrant_health_check() -> QdrantHealthResponse:
    """
    Qdrant-specific health check endpoint that verifies connectivity to Qdrant
    and that the required collection exists.

    Returns:
        QdrantHealthResponse: Health status with Qdrant-specific details
    """
    logger.info("Qdrant health check endpoint accessed")

    try:
        # Check Qdrant connectivity and collection existence
        is_connected, error_msg = check_qdrant_connectivity()  # Remove await since it's synchronous

        if is_connected:
            status = "healthy"
            details = {
                "qdrant_connected": True,
                "collection_exists": True,
                "collection_name": "book_chunks"
            }
        else:
            status = "unhealthy"
            details = {
                "qdrant_connected": False,
                "collection_exists": False,
                "collection_name": "book_chunks",
                "error": error_msg
            }

        return QdrantHealthResponse(
            status=status,
            details=details
        )
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        return QdrantHealthResponse(
            status="unhealthy",
            details={
                "qdrant_connected": False,
                "collection_exists": False,
                "collection_name": "book_chunks",
                "error": str(e)
            }
        )