"""Pack generator - creates ZIP files with all artifacts."""

import zipfile
from pathlib import Path
from typing import List, Optional

from internal.crypto.hash import compute_sha256
from internal.crypto.sign import get_or_create_keypair, sign_data
from internal.pack.manifest import Manifest


class PackGenerator:
    """Generate case packs (ZIP files)."""

    def __init__(self, base_path: Path, key_path: Path, key_name: str):
        """Initialize pack generator."""
        self.base_path = Path(base_path)
        self.key_path = Path(key_path)
        self.key_name = key_name

    def create_pack(
        self,
        case_id: str,
        manifest: Manifest,
        artifacts: List[Path],
        chain_of_custody_path: Optional[Path] = None,
    ) -> Path:
        """Create pack ZIP file."""
        pack_path = self.base_path / f"{case_id}" / "pack.zip"
        pack_path.parent.mkdir(parents=True, exist_ok=True)

        # Get or create signing keypair
        private_key, public_key = get_or_create_keypair(self.key_path, self.key_name)

        # Create canonical manifest JSON
        manifest_json = manifest.to_json(canonical=True)
        manifest_bytes = manifest_json.encode("utf-8")

        # Sign manifest
        signature = sign_data(private_key, manifest_bytes)

        # Write manifest and signature
        manifest_path = pack_path.parent / "manifest.json"
        manifest_path.write_text(manifest_json, encoding="utf-8")

        sig_path = pack_path.parent / "manifest.sig"
        sig_path.write_bytes(signature)

        # Write public key
        from cryptography.hazmat.primitives import serialization
        pubkey_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        pubkey_path = pack_path.parent / "pubkey.pem"
        pubkey_path.write_bytes(pubkey_pem)

        # Create ZIP file
        with zipfile.ZipFile(pack_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add manifest
            zipf.write(manifest_path, "manifest.json")

            # Add signature
            zipf.write(sig_path, "manifest.sig")

            # Add public key
            zipf.write(pubkey_path, "pubkey.pem")

            # Add artifacts
            for artifact_path in artifacts:
                if artifact_path.exists():
                    # Use relative path in ZIP
                    arcname = artifact_path.name
                    zipf.write(artifact_path, arcname)

            # Add chain of custody if provided
            if chain_of_custody_path and chain_of_custody_path.exists():
                zipf.write(chain_of_custody_path, "chain_of_custody.log")

        # Clean up temporary files
        manifest_path.unlink()
        sig_path.unlink()
        pubkey_path.unlink()

        return pack_path



