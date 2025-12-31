"""
Basic FastAPI app tests for the backend service.

This module contains tests for the main FastAPI application functionality,
including the root endpoint and basic application setup.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_app_instance_creation():
    """Test that the FastAPI app instance is created successfully."""
    assert app is not None
    assert hasattr(app, 'routes')


def test_root_endpoint_exists():
    """Test that the root endpoint exists and returns expected structure."""
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200

    # Check that response has the expected keys
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["message"] == "PIAIC71-Hackathon1-v1 Backend Service"
    assert data["status"] == "running"


def test_root_endpoint_content():
    """Test that the root endpoint returns correct content."""
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    # Verify structure and content
    assert isinstance(data, dict)
    assert "message" in data
    assert "status" in data
    assert isinstance(data["message"], str)
    assert isinstance(data["status"], str)


def test_app_has_health_router():
    """Test that the health router is included in the app."""
    # Check that health routes are registered
    route_paths = [route.path for route in app.routes]

    # The health and ready endpoints should be in the routes
    assert "/health" in route_paths
    assert "/ready" in route_paths


def test_app_title_set():
    """Test that the app has the correct title set."""
    assert app.title == "PIAIC71-Hackathon1-v1 Backend API"


def test_app_description_set():
    """Test that the app has the correct description set."""
    # Check if description is set in the app
    assert hasattr(app, 'description')
    assert app.description == "Backend service for the PIAIC71 Hackathon project"


def test_app_version_set():
    """Test that the app has the correct version set."""
    assert app.version == "0.1.0"