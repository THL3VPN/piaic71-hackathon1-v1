"""
CORS middleware configuration for GitHub Pages integration.

This module provides the CORS configuration needed to allow requests
from GitHub Pages origins while restricting access from other origins.
"""
from typing import Dict, List, Union
from ..config import settings


def get_cors_config(settings_obj=None) -> Dict[str, Union[List[str], bool]]:
    """
    Get CORS configuration for GitHub Pages origins.

    Args:
        settings_obj: Optional settings object to use instead of global settings

    Returns:
        Dict[str, Union[List[str], bool]]: CORS configuration
    """
    if settings_obj is None:
        settings_obj = settings

    # Construct allowed origins based on the configured GitHub Pages origin
    allowed_origins = [settings_obj.github_pages_origin]

    # Add common GitHub Pages patterns if not already included
    # Handle both user and organization pages
    if ".github.io" in settings_obj.github_pages_origin:
        username = settings_obj.github_pages_origin.split(".github.io")[0].split("//")[-1]
        if username and username != "your-username":
            user_pages_origin = f"https://{username}.github.io"
            if user_pages_origin not in allowed_origins:
                allowed_origins.append(user_pages_origin)

    # Ensure we have at least basic origins for development
    if "localhost" not in settings_obj.github_pages_origin:
        allowed_origins.extend([
            "http://localhost:3000",  # Common frontend dev server
            "http://localhost:8000",  # Local backend
            "http://127.0.0.1:3000",  # IPv4 localhost
            "http://127.0.0.1:8000",  # IPv4 backend
        ])

    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],  # Allow all methods
        "allow_headers": ["*"],  # Allow all headers
        "max_age": 86400,  # Cache preflight requests for 24 hours
    }


def get_allowed_origins_list(settings_obj=None) -> List[str]:
    """
    Get the list of allowed origins for CORS configuration.

    Args:
        settings_obj: Optional settings object to use instead of global settings

    Returns:
        List[str]: List of allowed origin URLs
    """
    return get_cors_config(settings_obj)["allow_origins"]