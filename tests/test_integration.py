"""Integration tests for the ingestion pipeline."""

import tempfile
from pathlib import Path

import pytest

from internal.config import Config
from internal.pipeline import IngestionPipeline


@pytest.mark.asyncio
async def test_pipeline_ingest_simple():
    """Test basic pipeline ingestion (mocked)."""
    # This is a simplified test - in real tests, we'd mock HTTP requests
    with tempfile.TemporaryDirectory() as tmpdir:
        from internal.config import (
            APIConfig,
            ClassifyConfig,
            CryptoConfig,
            PIIConfig,
            RetentionConfig,
            StorageConfig,
        )

        config = Config(
            seed_urls=[],
            storage=StorageConfig(
                base_path=str(Path(tmpdir) / "data"),
                vault_path=str(Path(tmpdir) / "vault"),
                sqlite_path=str(Path(tmpdir) / "test.db"),
            ),
            crypto=CryptoConfig(
                key_path=str(Path(tmpdir) / "keys"),
                key_name="test-key",
            ),
            pii=PIIConfig(
                hmac_key="test-hmac-key-for-deterministic-pseudonymization-12345",
                languages=["en"],
            ),
            classify=ClassifyConfig(
                ml_endpoint="http://localhost:8001/classify",
                timeout=30,
            ),
            api=APIConfig(),
            retention=RetentionConfig(),
        )

        pipeline = IngestionPipeline(config)

        # Note: This would require mocking httpx for actual testing
        # For now, we just test that the pipeline can be initialized
        assert pipeline is not None
        assert pipeline.case_store is not None
        assert pipeline.vault is not None

        await pipeline.close()

