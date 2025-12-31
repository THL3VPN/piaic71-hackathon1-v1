"""
Test configuration for the backend service tests.

This module contains shared test fixtures and configuration that can be used
across all test modules in the backend service.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_settings():
    """Provide sample settings for testing purposes."""
    return {
        "backend_host": "localhost",
        "backend_port": 8000,
        "neon_database_url": "postgresql://test:test@localhost:5432/testdb",
        "qdrant_url": "http://localhost:6333",
        "github_pages_origin": "https://test-user.github.io",
        "log_level": "INFO",
        "request_timeout": 30000,
        "root_path": ""
    }