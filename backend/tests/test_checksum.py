"""
Tests for checksum utilities.
"""
import pytest
import tempfile
import os
from app.utils.checksum import calculate_sha256, verify_checksum, calculate_file_checksum


def test_calculate_sha256_string():
    """Test calculating SHA-256 for string content."""
    content = "Hello, World!"
    expected_checksum = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    checksum = calculate_sha256(content)

    assert checksum == expected_checksum


def test_calculate_sha256_bytes():
    """Test calculating SHA-256 for bytes content."""
    content = b"Hello, World!"
    expected_checksum = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    checksum = calculate_sha256(content)

    assert checksum == expected_checksum


def test_calculate_sha256_empty():
    """Test calculating SHA-256 for empty content."""
    content = ""
    expected_checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    checksum = calculate_sha256(content)

    assert checksum == expected_checksum


def test_verify_checksum_valid():
    """Test verifying a valid checksum."""
    content = "Hello, World!"
    checksum = calculate_sha256(content)

    is_valid = verify_checksum(content, checksum)

    assert is_valid is True


def test_verify_checksum_invalid():
    """Test verifying an invalid checksum."""
    content = "Hello, World!"
    wrong_checksum = "invalid_checksum_here"

    is_valid = verify_checksum(content, wrong_checksum)

    assert is_valid is False


def test_calculate_file_checksum():
    """Test calculating SHA-256 for a file."""
    content = "This is test file content for checksum testing."

    # Create a temporary file with the content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Calculate file checksum
        file_checksum = calculate_file_checksum(temp_file_path)

        # Calculate expected checksum for comparison
        expected_checksum = calculate_sha256(content)

        assert file_checksum == expected_checksum
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_calculate_file_checksum_empty():
    """Test calculating SHA-256 for an empty file."""
    content = ""
    expected_checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Create a temporary empty file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        file_checksum = calculate_file_checksum(temp_file_path)
        assert file_checksum == expected_checksum
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_checksum_consistency():
    """Test that string and file checksums are consistent for the same content."""
    content = "Consistency test content"

    # Calculate checksum directly from string
    string_checksum = calculate_sha256(content)

    # Write content to a temporary file and calculate checksum
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        file_checksum = calculate_file_checksum(temp_file_path)

        # Both checksums should be identical
        assert string_checksum == file_checksum
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_checksum_deterministic():
    """Test that checksums are deterministic - same content always produces same checksum."""
    content = "Deterministic test content"

    checksum1 = calculate_sha256(content)
    checksum2 = calculate_sha256(content)
    checksum3 = calculate_sha256(content)

    assert checksum1 == checksum2 == checksum3


def test_different_content_different_checksums():
    """Test that different content produces different checksums."""
    content1 = "Content one"
    content2 = "Content two"

    checksum1 = calculate_sha256(content1)
    checksum2 = calculate_sha256(content2)

    assert checksum1 != checksum2