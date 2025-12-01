"""Mock HTTP responses for testing."""

from unittest.mock import Mock

import httpx


def create_mock_html_response(html_content: str, status_code: int = 200) -> Mock:
    """Create a mock HTTP response with HTML content."""
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    response.text = html_content
    response.content = html_content.encode("utf-8")
    response.headers = {"content-type": "text/html; charset=utf-8"}
    response.url = "https://example.com"
    response.raise_for_status = Mock()
    return response


def create_mock_image_response(image_data: bytes, status_code: int = 200) -> Mock:
    """Create a mock HTTP response with image content."""
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    response.content = image_data
    response.headers = {"content-type": "image/png"}
    response.url = "https://example.com/image.png"
    response.raise_for_status = Mock()
    return response


def create_mock_classifier_response(classification_data: dict) -> Mock:
    """Create a mock classifier API response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = classification_data
    response.raise_for_status = Mock()
    return response

