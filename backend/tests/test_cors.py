"""
CORS middleware tests for the backend service.

This module contains tests for the CORS middleware functionality,
verifying that it properly allows GitHub Pages origins while restricting others.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.middleware.cors import get_cors_config


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_cors_config_structure():
    """Test that CORS configuration has the expected structure and values."""
    from app.config import settings

    cors_config = get_cors_config(settings)

    # Check that it has the required CORS configuration keys
    assert "allow_origins" in cors_config
    assert "allow_credentials" in cors_config
    assert "allow_methods" in cors_config
    assert "allow_headers" in cors_config

    # Check that GitHub Pages origin is included in allowed origins
    assert settings.github_pages_origin in cors_config["allow_origins"]

    # Check default values
    assert cors_config["allow_credentials"] is True
    assert "*" in cors_config["allow_methods"]  # Should allow all methods
    assert "*" in cors_config["allow_headers"]  # Should allow all headers


def test_cors_config_with_github_pages_origin():
    """Test CORS configuration with a specific GitHub Pages origin."""
    from app.config import settings
    from pydantic_settings import BaseSettings

    # Create custom settings with a specific GitHub Pages origin
    class TestSettings(BaseSettings):
        github_pages_origin: str = "https://testuser.github.io"

        class Config:
            env_file = ".env"
            env_file_encoding = 'utf-8'

    test_settings = TestSettings()
    cors_config = get_cors_config(test_settings)

    assert "https://testuser.github.io" in cors_config["allow_origins"]


def test_cors_preflight_request_allowed():
    """Test that CORS preflight requests are allowed for GitHub Pages origin."""
    from app.config import settings

    # Test preflight request (OPTIONS) from GitHub Pages origin
    with TestClient(app) as client:
        response = client.options(
            "/",
            headers={
                "Origin": settings.github_pages_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Requested-With",
            }
        )

        # Preflight should be allowed
        assert response.status_code in [200, 204]  # 200 or 204 for successful preflight

        # Check for CORS headers in response
        assert "access-control-allow-origin" in response.headers


def test_cors_github_pages_origin_allowed():
    """Test that requests from GitHub Pages origin are allowed."""
    from app.config import settings

    with TestClient(app) as client:
        response = client.get(
            "/",
            headers={
                "Origin": settings.github_pages_origin,
                "Host": "localhost:8000"
            }
        )

        # Request should be successful
        assert response.status_code == 200

        # Check for CORS headers in response
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == settings.github_pages_origin


def test_cors_other_origins_restricted():
    """Test that requests from non-GitHub Pages origins are restricted."""
    with TestClient(app) as client:
        response = client.get(
            "/",
            headers={
                "Origin": "https://malicious-site.com",
                "Host": "localhost:8000"
            }
        )

        # The request might still succeed (server processes it) but CORS headers should not allow it in browser
        # Check that the response doesn't include the malicious origin in access-control-allow-origin
        if "access-control-allow-origin" in response.headers:
            from app.config import settings
            assert response.headers["access-control-allow-origin"] != "https://malicious-site.com"
            # Should either not have the header or have the default origin
        else:
            # If no CORS header is present, the browser will block the request
            pass


def test_cors_header_inclusion():
    """Test that CORS headers are properly included in responses."""
    from app.config import settings

    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={
                "Origin": settings.github_pages_origin,
            }
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == settings.github_pages_origin


def test_cors_credentials_allowed():
    """Test that credentials are allowed in CORS requests."""
    from app.config import settings

    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={
                "Origin": settings.github_pages_origin,
                "Cookie": "session=test"
            }
        )

        assert response.status_code == 200
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_methods_allowed():
    """Test that all HTTP methods are allowed in CORS configuration."""
    from app.config import settings

    # Test various HTTP methods from GitHub Pages origin
    methods_to_test = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    with TestClient(app) as client:
        for method in methods_to_test:
            # Create a request with the specific method
            if method == "GET":
                response = getattr(client, "get")(
                    "/health",
                    headers={"Origin": settings.github_pages_origin}
                )
            elif method == "POST":
                response = getattr(client, "post")(
                    "/health",
                    headers={"Origin": settings.github_pages_origin}
                )
            elif method == "PUT":
                response = getattr(client, "put")(
                    "/health",
                    headers={"Origin": settings.github_pages_origin}
                )
            elif method == "DELETE":
                response = getattr(client, "delete")(
                    "/health",
                    headers={"Origin": settings.github_pages_origin}
                )
            elif method == "PATCH":
                response = getattr(client, "patch")(
                    "/health",
                    headers={"Origin": settings.github_pages_origin}
                )

            # The request should not be blocked by CORS
            # Note: Non-GET/POST methods might return 405 Method Not Allowed for the endpoint,
            # but they should not be blocked by CORS itself
            if response.status_code == 405:  # Method Not Allowed for the endpoint
                continue  # This is expected for endpoints that don't support the method
            else:
                assert response.status_code in [200, 404, 422]  # Should not be blocked by CORS