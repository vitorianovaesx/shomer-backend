"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from tests.fixtures.sample_data import (
    MOCK_CLASSIFIER_RESPONSE,
    SAMPLE_HTML_NO_PII,
    SAMPLE_HTML_WITH_PII,
    SAMPLE_TEXT_NO_PII,
    SAMPLE_TEXT_WITH_PII,
    TEST_IMAGE_URLS,
    TEST_URLS,
)


@pytest.fixture
def sample_html_no_pii():
    """Fixture for HTML content without PII."""
    return SAMPLE_HTML_NO_PII


@pytest.fixture
def sample_html_with_pii():
    """Fixture for HTML content with PII."""
    return SAMPLE_HTML_WITH_PII


@pytest.fixture
def sample_text_no_pii():
    """Fixture for text content without PII."""
    return SAMPLE_TEXT_NO_PII


@pytest.fixture
def sample_text_with_pii():
    """Fixture for text content with PII."""
    return SAMPLE_TEXT_WITH_PII


@pytest.fixture
def test_urls():
    """Fixture for test URLs."""
    return TEST_URLS


@pytest.fixture
def test_image_urls():
    """Fixture for test image URLs."""
    return TEST_IMAGE_URLS


@pytest.fixture
def mock_classifier_response():
    """Fixture for mock classifier response."""
    return MOCK_CLASSIFIER_RESPONSE


@pytest.fixture
def hmac_key():
    """Fixture for HMAC key used in tests."""
    return "test-hmac-key-for-deterministic-pseudonymization-12345678901234567890123456789012"
