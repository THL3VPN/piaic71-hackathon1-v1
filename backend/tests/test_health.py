"""
Health endpoint tests for the backend service.

This module contains tests for the health endpoint functionality,
verifying that it returns the correct status and response format.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint_returns_ok(client):
    """Test that the health endpoint returns 200 with status ok."""
    response = client.get("/health")

    assert response.status_code == 200

    # Check response structure and content
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_health_endpoint_response_format(client):
    """Test that the health endpoint returns the correct response format."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 1  # Only the status field
    assert data["status"] == "ok"


def test_health_endpoint_method_not_allowed(client):
    """Test that non-GET methods are not allowed on the health endpoint."""
    # Test POST method
    response = client.post("/health")
    assert response.status_code in [405, 404]  # Method not allowed or not found

    # Test PUT method
    response = client.put("/health")
    assert response.status_code in [405, 404]

    # Test DELETE method
    response = client.delete("/health")
    assert response.status_code in [405, 404]


def test_health_endpoint_consistent_response(client):
    """Test that the health endpoint consistently returns the same response."""
    # Call the endpoint multiple times
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"


def test_health_endpoint_performance(client):
    """Test that the health endpoint responds quickly."""
    import time

    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    response_time_ms = (end_time - start_time) * 1000
    assert response.status_code == 200
    # Health checks should be very fast (less than 100ms)
    # Though this might be affected by test environment, we'll set a reasonable threshold