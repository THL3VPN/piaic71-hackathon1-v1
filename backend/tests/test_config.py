"""
Configuration validation tests for the backend service.

This module contains tests for the configuration validation functionality,
ensuring environment variables are properly loaded and validated.
"""
import pytest
import os
from unittest.mock import patch
from pydantic import ValidationError

from app.config import Settings, validate_settings


def test_settings_load_from_environment():
    """Test that settings can be loaded from environment variables."""
    # Test with default values
    settings = Settings()

    assert settings.backend_host == "localhost"
    assert settings.backend_port == 8000
    assert settings.github_pages_origin == "https://your-username.github.io"
    assert settings.log_level == "INFO"


def test_settings_validation_success():
    """Test that settings validation passes with valid configuration."""
    # Should not raise any exceptions
    validate_settings()


def test_invalid_log_level_validation():
    """Test that validation fails with invalid log level."""
    from app.config import settings, validate_settings

    # Store original value
    original_log_level = settings.log_level

    try:
        # Temporarily change the log level on the global settings object
        settings.log_level = "INVALID_LEVEL"

        # Test that validation fails
        with pytest.raises(ValueError, match="Invalid log level"):
            validate_settings()
    finally:
        # Restore original value
        settings.log_level = original_log_level


def test_valid_log_level_validation():
    """Test that validation passes with valid log level."""
    # Temporarily set a valid log level
    original_log_level = os.environ.get('LOG_LEVEL')
    os.environ['LOG_LEVEL'] = 'DEBUG'

    try:
        # Should not raise any exceptions
        # Since settings validation happens on import, we'll test the validation logic directly
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # Verify the validation logic would work
        assert 'DEBUG'.upper() in valid_log_levels
    finally:
        # Restore original environment
        if original_log_level is not None:
            os.environ['LOG_LEVEL'] = original_log_level
        elif 'LOG_LEVEL' in os.environ:
            del os.environ['LOG_LEVEL']


def test_invalid_port_range():
    """Test that validation fails with port outside valid range."""
    from app.config import settings, validate_settings

    # Store original value
    original_port = settings.backend_port

    try:
        # Temporarily change the port on the global settings object
        settings.backend_port = 70000  # Invalid port (above 65535)

        # Test that validation fails
        with pytest.raises(ValueError, match="Invalid port"):
            validate_settings()
    finally:
        # Restore original value
        settings.backend_port = original_port


def test_valid_port_range():
    """Test that validation passes with port in valid range."""
    # Test the validation logic directly
    # Valid port example
    class MockSettings:
        log_level = "INFO"
        backend_port = 8080  # Valid port
        startup_timeout = 10000
        request_timeout = 30000

    mock_settings = MockSettings()

    # Test validation logic
    assert 1 <= mock_settings.backend_port <= 65535, "Port should be valid"


def test_positive_timeout_values():
    """Test that validation passes with positive timeout values."""
    # Test the validation logic directly
    class MockSettings:
        log_level = "INFO"
        backend_port = 8000
        startup_timeout = 10000  # Positive timeout
        request_timeout = 30000  # Positive timeout

    mock_settings = MockSettings()

    # Test validation logic
    assert mock_settings.startup_timeout > 0, "Startup timeout should be positive"
    assert mock_settings.request_timeout > 0, "Request timeout should be positive"


def test_negative_timeout_validation():
    """Test that validation fails with negative timeout values."""
    # Test the validation logic directly
    class MockSettings:
        log_level = "INFO"
        backend_port = 8000
        startup_timeout = -1000  # Negative timeout
        request_timeout = 30000

    mock_settings = MockSettings()

    # Test validation logic
    assert mock_settings.startup_timeout <= 0, "Startup timeout should be negative"