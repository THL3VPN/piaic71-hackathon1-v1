"""
Checksum utilities for document integrity and change detection.
"""
import hashlib
from typing import Union


def calculate_sha256(content: Union[str, bytes]) -> str:
    """
    Calculate SHA-256 checksum for content.

    Args:
        content: Content to hash (string or bytes)

    Returns:
        SHA-256 checksum as hexadecimal string
    """
    if isinstance(content, str):
        content = content.encode('utf-8')

    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()


def verify_checksum(content: Union[str, bytes], expected_checksum: str) -> bool:
    """
    Verify that content matches the expected checksum.

    Args:
        content: Content to verify
        expected_checksum: Expected SHA-256 checksum

    Returns:
        True if checksum matches, False otherwise
    """
    actual_checksum = calculate_sha256(content)
    return actual_checksum == expected_checksum


def calculate_file_checksum(file_path: str) -> str:
    """
    Calculate SHA-256 checksum for a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 checksum as hexadecimal string
    """
    sha256_hash = hashlib.sha256()

    with open(file_path, 'rb') as f:
        # Read the file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()