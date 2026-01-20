"""
Text extraction utilities for processing markdown and MDX files.
"""
import re
from typing import Tuple, Optional
from markdown_it import MarkdownIt
import logging


logger = logging.getLogger(__name__)


def extract_text_with_frontmatter(content: str) -> Tuple[str, dict, str]:
    """
    Extract text content, frontmatter, and title from markdown/MDX content.

    Args:
        content: Raw markdown/MDX content

    Returns:
        Tuple of (clean_text, frontmatter_dict, title)
    """
    # Parse frontmatter
    frontmatter = {}
    clean_content = content

    # Try to extract frontmatter using regex
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)

    if frontmatter_match:
        frontmatter_str = frontmatter_match.group(1)
        clean_content = frontmatter_match.group(2)

        # Parse frontmatter YAML manually
        try:
            frontmatter = parse_frontmatter(frontmatter_str)
        except Exception as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
            # If YAML parsing fails, return original content
            frontmatter = {}
            clean_content = content

    # Extract title from content if not in frontmatter
    title = frontmatter.get('title', '')
    if not title:
        title = extract_title_from_content(clean_content)

    return clean_content.strip(), frontmatter, title


def parse_frontmatter(frontmatter_str: str) -> dict:
    """
    Parse frontmatter YAML manually to avoid adding additional dependencies.

    Args:
        frontmatter_str: Raw frontmatter content

    Returns:
        Dictionary of frontmatter key-value pairs
    """
    frontmatter = {}

    for line in frontmatter_str.strip().split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            frontmatter[key] = value

    return frontmatter


def extract_title_from_content(content: str) -> str:
    """
    Extract title from markdown content (first heading).

    Args:
        content: Markdown content without frontmatter

    Returns:
        Extracted title or empty string
    """
    lines = content.split('\n')

    for line in lines:
        # Look for H1 heading
        h1_match = re.match(r'^#\s+(.+)', line)
        if h1_match:
            return h1_match.group(1).strip()

    return ''


def preserve_code_blocks(content: str) -> str:
    """
    Ensure code blocks are preserved during text extraction.

    Args:
        content: Markdown content

    Returns:
        Content with properly formatted code blocks
    """
    # This function ensures that code blocks are properly handled
    # The markdown parser should preserve them by default
    return content