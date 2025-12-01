"""Tests for chain of custody logging."""

import json
import tempfile
from pathlib import Path

import pytest

from internal.custody.logger import ChainOfCustodyLogger


def test_custody_logger():
    """Test chain of custody logging."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
        log_path = Path(f.name)

    try:
        logger = ChainOfCustodyLogger(log_path)

        # Log events
        logger.log("case-123", "created", actor="system")
        logger.log("case-123", "fetched", status="success")
        logger.log("case-123", "pii-detected", metadata={"count": 2})

        # Get events
        events = logger.get_events("case-123")
        assert len(events) == 3
        assert events[0]["action"] == "created"
        assert events[1]["status"] == "success"
        assert events[2]["metadata"]["count"] == 2

        # Test error logging
        logger.log("case-123", "failed", status="error", error="Test error")
        events = logger.get_events("case-123")
        assert events[-1]["status"] == "error"
        assert events[-1]["error"] == "Test error"
    finally:
        log_path.unlink()


def test_custody_logger_no_pii():
    """Test that logs don't contain PII."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
        log_path = Path(f.name)

    try:
        logger = ChainOfCustodyLogger(log_path)

        # Log with metadata (should not contain PII)
        logger.log(
            "case-123",
            "pii-moved",
            metadata={"vault_ref": "vault-123", "type": "text"},
        )

        # Read log file
        with open(log_path, "r") as f:
            log_content = f.read()

        # Should not contain actual PII (emails, phones, etc.)
        # Metadata should only contain references, not actual content
        assert "vault_ref" in log_content
        assert "@" not in log_content  # No emails in logs
    finally:
        log_path.unlink()



