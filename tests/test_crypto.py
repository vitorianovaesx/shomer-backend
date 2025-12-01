"""Tests for cryptographic utilities."""

import tempfile
from pathlib import Path

import pytest

from internal.crypto.hash import compute_sha256, hash_file
from internal.crypto.sign import (
    generate_keypair,
    get_or_create_keypair,
    sign_data,
    verify_signature,
)


def test_compute_sha256():
    """Test SHA256 computation."""
    data = b"test data"
    hash1 = compute_sha256(data)
    hash2 = compute_sha256(data)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex string length


def test_hash_file():
    """Test file hashing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = Path(f.name)

    try:
        hash1 = hash_file(temp_path)
        hash2 = hash_file(temp_path)

        assert hash1 == hash2
        assert len(hash1) == 64
    finally:
        temp_path.unlink()


def test_keypair_generation():
    """Test Ed25519 keypair generation."""
    private_key, public_key = generate_keypair()

    assert private_key is not None
    assert public_key is not None


def test_sign_and_verify():
    """Test signing and verification."""
    private_key, public_key = generate_keypair()
    data = b"test data to sign"

    signature = sign_data(private_key, data)

    assert verify_signature(public_key, signature, data) is True
    assert verify_signature(public_key, signature, b"wrong data") is False


def test_get_or_create_keypair():
    """Test keypair persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir)
        key_name = "test-key"

        # First call should create keypair
        private_key1, public_key1 = get_or_create_keypair(key_path, key_name)

        # Second call should load existing keypair
        private_key2, public_key2 = get_or_create_keypair(key_path, key_name)

        # Sign with first keypair
        data = b"test data"
        signature = sign_data(private_key1, data)

        # Verify with second keypair (should work if same keys)
        assert verify_signature(public_key2, signature, data) is True


