"""
Tests for text extraction utilities.
"""
import pytest
from app.utils.text_extractor import extract_text_with_frontmatter


def test_extract_text_with_frontmatter():
    """Test extracting text and frontmatter from markdown content."""
    content = """---
title: Test Document
author: Test Author
---
# This is a test document

This is the content of the document.

## Section 1
Some content here.
"""

    clean_text, frontmatter, title = extract_text_with_frontmatter(content)

    # Check that frontmatter was extracted
    assert 'title' in frontmatter
    assert 'author' in frontmatter
    assert frontmatter['title'] == 'Test Document'
    assert frontmatter['author'] == 'Test Author'

    # Check that title was extracted from frontmatter
    assert title == 'Test Document'

    # Check that clean text doesn't include frontmatter
    assert '---' not in clean_text
    assert 'title:' not in clean_text
    assert 'author:' not in clean_text
    assert '# This is a test document' in clean_text


def test_extract_title_from_content():
    """Test extracting title from markdown content when not in frontmatter."""
    content = """# This is the Title

Some content here.

## Section 1
More content.
"""

    clean_text, frontmatter, title = extract_text_with_frontmatter(content)

    # Since no frontmatter, title should be extracted from content
    assert title == 'This is the Title'
    assert not frontmatter  # No frontmatter should be found


def test_extract_text_preserves_code_blocks():
    """Test that code blocks are preserved during extraction."""
    content = """---
title: Code Test
---
# Code Test Document

Here is some code:

```python
def hello_world():
    print("Hello, World!")
```

And more content.
"""

    clean_text, frontmatter, title = extract_text_with_frontmatter(content)

    # Check that frontmatter was extracted
    assert frontmatter['title'] == 'Code Test'

    # Check that code block is preserved in the clean text
    assert 'def hello_world():' in clean_text
    assert 'print("Hello, World!")' in clean_text
    assert '```python' in clean_text


def test_extract_text_with_empty_frontmatter():
    """Test extracting text when frontmatter is empty or malformed."""
    content = """---
---
# Document with empty frontmatter

Content here.
"""

    clean_text, frontmatter, title = extract_text_with_frontmatter(content)

    # Frontmatter is empty, so dict should be empty
    assert frontmatter == {}

    # Title should be extracted from content
    assert title == 'Document with empty frontmatter'

    # Clean text should not include frontmatter
    assert '---' not in clean_text


def test_extract_text_no_frontmatter():
    """Test extracting text when there's no frontmatter."""
    content = """# Document without frontmatter

This document has no frontmatter.

## Section
Some content.
"""

    clean_text, frontmatter, title = extract_text_with_frontmatter(content)

    # No frontmatter should be found
    assert frontmatter == {}

    # Title should be extracted from content
    assert title == 'Document without frontmatter'

    # Clean text should be the same as input
    assert '# Document without frontmatter' in clean_text
    assert 'This document has no frontmatter.' in clean_text