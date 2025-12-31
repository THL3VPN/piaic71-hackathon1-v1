"""
Main FastAPI application for the backend service.

This module initializes the FastAPI application with proper configuration,
middleware, and API routes for health and readiness endpoints.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, validate_settings
from . import health
from .middleware.cors import get_cors_config

# Load and validate settings at startup
settings = Settings()
validate_settings()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Log startup information
logger.info("Starting PIAIC71-Hackathon1-v1 Backend Service")
logger.info(f"Backend host: {settings.backend_host}")
logger.info(f"Backend port: {settings.backend_port}")
logger.info(f"GitHub Pages origin: {settings.github_pages_origin}")
logger.info(f"Log level: {settings.log_level}")

# Initialize FastAPI app
app = FastAPI(
    title="PIAIC71-Hackathon1-v1 Backend API",
    description="Backend service for the PIAIC71 Hackathon project",
    version="0.1.0",
    root_path=settings.root_path if settings.root_path else None
)

# Add CORS middleware for GitHub Pages
cors_config = get_cors_config(settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
    max_age=cors_config.get("max_age", 86400),
    # Additional security: only expose headers that are meant to be accessible
    # expose_headers=["Access-Control-Allow-Origin"]
)

# Include routers
app.include_router(health.router, prefix="", tags=["health"])

@app.get("/")
async def root():
    """
    Root endpoint for the backend service.
    """
    return {"message": "PIAIC71-Hackathon1-v1 Backend Service", "status": "running"}