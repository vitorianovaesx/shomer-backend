"""Tests for PII detection and pseudonymization."""

import pytest

from internal.pii.detector import PIIDetector
from internal.pii.pseudonymizer import Pseudonymizer


def test_pii_detector_basic():
    """Test basic PII detection."""
    detector = PIIDetector(languages=["en"])

    # Test email detection
    text_with_email = "Contact us at test@example.com for more info."
    detections = detector.detect(text_with_email)
    assert len(detections) > 0

    # Test phone detection
    text_with_phone = "Call us at 555-123-4567"
    detections = detector.detect(text_with_phone)
    assert len(detections) > 0

    # Test no PII
    text_no_pii = "This is a simple text without any personal information."
    detections = detector.detect(text_no_pii)
    # May or may not detect false positives, but should not crash


def test_pseudonymizer_deterministic():
    """Test deterministic pseudonymization."""
    hmac_key = "test-key-12345"
    pseudonymizer = Pseudonymizer(hmac_key)

    # Same input should produce same output
    value1 = pseudonymizer.pseudonymize("test@example.com", "EMAIL")
    value2 = pseudonymizer.pseudonymize("test@example.com", "EMAIL")

    assert value1 == value2
    assert value1.startswith("[EMA_")

    # Different input should produce different output
    value3 = pseudonymizer.pseudonymize("other@example.com", "EMAIL")
    assert value1 != value3


def test_pseudonymize_text():
    """Test text pseudonymization."""
    hmac_key = "test-key-12345"
    pseudonymizer = Pseudonymizer(hmac_key)
    detector = PIIDetector(languages=["en"])

    text = "Contact John Doe at john.doe@example.com or call 555-123-4567"
    detections = detector.detect(text)

    if detections:
        redacted = pseudonymizer.pseudonymize_text(text, detections)
        assert redacted != text
        # Should not contain original email
        assert "john.doe@example.com" not in redacted


def test_pseudonymizer_requires_key():
    """Test that pseudonymizer requires HMAC key."""
    with pytest.raises(ValueError):
        Pseudonymizer("")

