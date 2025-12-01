"""Tests for manifest generation."""

import tempfile
from pathlib import Path

import pytest

from internal.crypto.hash import hash_file
from internal.pack.manifest import Manifest


def test_manifest_creation():
    """Test manifest creation."""
    manifest = Manifest(
        case_id="test-case-123",
        url="https://example.com",
        artifacts=[],
        pii_detected=False,
    )

    assert manifest.case_id == "test-case-123"
    assert manifest.url == "https://example.com"
    assert manifest.pii_detected is False


def test_manifest_add_artifact():
    """Test adding artifacts to manifest."""
    manifest = Manifest(
        case_id="test-case-123",
        url="https://example.com",
    )

    manifest.add_artifact("text", "path/to/text.txt", "abc123")
    manifest.add_artifact("image", "path/to/image.jpg", "def456", vault_ref="vault-123")

    assert len(manifest.artifacts) == 2
    assert manifest.artifacts[0]["type"] == "text"
    assert manifest.artifacts[1]["vault_ref"] == "vault-123"


def test_manifest_canonical_json():
    """Test canonical JSON generation."""
    manifest1 = Manifest(
        case_id="test-case-123",
        url="https://example.com",
        artifacts=[{"type": "text", "path": "a.txt", "hash": "abc"}],
    )

    manifest2 = Manifest(
        case_id="test-case-123",
        url="https://example.com",
        artifacts=[{"type": "text", "path": "a.txt", "hash": "abc"}],
    )

    # Canonical JSON should be identical
    json1 = manifest1.to_json(canonical=True)
    json2 = manifest2.to_json(canonical=True)

    assert json1 == json2

    # Should be compact (no extra whitespace)
    assert "\n" not in json1
    assert "  " not in json1


def test_manifest_with_classification():
    """Test manifest with classification."""
    manifest = Manifest(
        case_id="test-case-123",
        url="https://example.com",
        classification={"classification": "positive", "confidence": 0.95},
    )

    data = manifest.to_dict()
    assert "classification" in data
    assert data["classification"]["classification"] == "positive"



