"""Encrypted vault for PII and images."""

import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

from cryptography.fernet import Fernet


class Vault:
    """Encrypted vault for storing sensitive content."""

    def __init__(self, vault_path: Path, key_path: Optional[Path] = None):
        """Initialize vault."""
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.key_path = key_path or self.vault_path / ".vault_key"

        # Use Fernet encryption for prototype
        # In production, this would use LUKS or proper age encryption
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
        else:
            key = self.key_path.read_bytes()

        self._cipher = Fernet(key)

    def store(self, content: bytes, metadata: Optional[dict] = None) -> str:
        """Store content in vault and return vault reference."""
        vault_ref = str(uuid4())
        vault_file = self.vault_path / f"{vault_ref}.enc"

        # Encrypt content
        encrypted = self._cipher.encrypt(content)
        vault_file.write_bytes(encrypted)

        # Store metadata if provided
        if metadata:
            meta_file = self.vault_path / f"{vault_ref}.meta"
            meta_file.write_text(json.dumps(metadata, indent=2))

        return vault_ref

    def retrieve(self, vault_ref: str) -> bytes:
        """Retrieve content from vault."""
        vault_file = self.vault_path / f"{vault_ref}.enc"

        if not vault_file.exists():
            raise FileNotFoundError(f"Vault reference not found: {vault_ref}")

        encrypted = vault_file.read_bytes()
        content = self._cipher.decrypt(encrypted)

        return content

    def get_metadata(self, vault_ref: str) -> Optional[dict]:
        """Get metadata for vault reference."""
        meta_file = self.vault_path / f"{vault_ref}.meta"
        if meta_file.exists():
            return json.loads(meta_file.read_text())
        return None

