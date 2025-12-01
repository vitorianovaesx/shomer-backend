"""Configuration management for Shomer backend."""

import os
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class StorageConfig(BaseModel):
    """Storage configuration."""

    base_path: str = "./data"
    vault_path: str = "./vault"
    sqlite_path: str = "./data/shomer.db"


class CryptoConfig(BaseModel):
    """Cryptographic configuration."""

    key_path: str = "./keys"
    key_name: str = "shomer-key"


class PIIConfig(BaseModel):
    """PII handling configuration."""

    hmac_key: str = ""
    languages: List[str] = ["en"]


class ClassifyConfig(BaseModel):
    """Classification configuration."""

    ml_endpoint: str = "http://localhost:8001/classify"
    timeout: int = 30


class APIConfig(BaseModel):
    """API configuration."""

    host: str = "0.0.0.0"
    port: int = 8000
    admin_token: str = ""


class RetentionConfig(BaseModel):
    """Retention policy configuration."""

    vault_originals: int = 730  # 2 years
    packs: int = 365  # 1 year
    manifests: int = 1825  # 5 years
    chain_of_custody: int = 2555  # 7 years


class Config(BaseModel):
    """Main configuration."""

    seed_urls: List[str] = Field(default_factory=list)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    crypto: CryptoConfig = Field(default_factory=CryptoConfig)
    pii: PIIConfig = Field(default_factory=PIIConfig)
    classify: ClassifyConfig = Field(default_factory=ClassifyConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    retention: RetentionConfig = Field(default_factory=RetentionConfig)


class Settings(BaseSettings):
    """Environment-based settings."""

    shomer_hmac_key: Optional[str] = None
    shomer_admin_token: Optional[str] = None

    class Config:
        env_file = ".env"
        env_prefix = "SHOMER_"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file and environment variables."""
    settings = Settings()

    if config_path is None:
        config_path = os.getenv("SHOMER_CONFIG", "config.yaml")

    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)
            config = Config(**config_data)
    else:
        config = Config()

    # Override with environment variables
    if settings.shomer_hmac_key:
        config.pii.hmac_key = settings.shomer_hmac_key
    if settings.shomer_admin_token:
        config.api.admin_token = settings.shomer_admin_token

    # Ensure directories exist
    Path(config.storage.base_path).mkdir(parents=True, exist_ok=True)
    Path(config.storage.vault_path).mkdir(parents=True, exist_ok=True)
    Path(config.crypto.key_path).mkdir(parents=True, exist_ok=True)

    return config



