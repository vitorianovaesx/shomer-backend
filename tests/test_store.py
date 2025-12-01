"""Tests for storage layer."""

import tempfile
from pathlib import Path

import pytest

from internal.store.case_store import CaseStore
from internal.store.vault import Vault


def test_case_store():
    """Test case storage."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    try:
        store = CaseStore(db_path)

        # Create case
        case_id = store.create_case("https://example.com")
        assert case_id is not None

        # Get case
        case = store.get_case(case_id)
        assert case is not None
        assert case["url"] == "https://example.com"
        assert case["status"] == "created"

        # Update case
        store.update_case_status(case_id, "completed", manifest_hash="abc123")
        case = store.get_case(case_id)
        assert case["status"] == "completed"
        assert case["manifest_hash"] == "abc123"

        # Add artifact
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            artifact_path = Path(f.name)

        try:
            artifact_id = store.add_artifact(
                case_id, "text", artifact_path, vault_ref="vault-ref-123"
            )
            assert artifact_id is not None

            # Get artifacts
            artifacts = store.get_artifacts(case_id)
            assert len(artifacts) == 1
            assert artifacts[0]["artifact_type"] == "text"
            assert artifacts[0]["vault_ref"] == "vault-ref-123"
        finally:
            artifact_path.unlink()
    finally:
        db_path.unlink()


def test_vault():
    """Test vault storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        vault = Vault(vault_path)

        # Store content
        content = b"secret content"
        vault_ref = vault.store(content, metadata={"type": "test"})

        assert vault_ref is not None

        # Retrieve content
        retrieved = vault.retrieve(vault_ref)
        assert retrieved == content

        # Get metadata
        metadata = vault.get_metadata(vault_ref)
        assert metadata is not None
        assert metadata["type"] == "test"

        # Test non-existent reference
        with pytest.raises(FileNotFoundError):
            vault.retrieve("non-existent-ref")


