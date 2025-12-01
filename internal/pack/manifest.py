"""Manifest generation in JCS (JSON Canonicalization Scheme) format."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from internal.crypto.hash import hash_file


class Manifest:
    """Canonical manifest for a case."""

    def __init__(
        self,
        case_id: str,
        url: str,
        created_at: Optional[str] = None,
        artifacts: Optional[List[Dict[str, Any]]] = None,
        classification: Optional[Dict[str, Any]] = None,
        pii_detected: bool = False,
    ):
        """Initialize manifest."""
        self.case_id = case_id
        self.url = url
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.artifacts = artifacts or []
        self.classification = classification
        self.pii_detected = pii_detected

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        manifest = {
            "case_id": self.case_id,
            "url": self.url,
            "created_at": self.created_at,
            "artifacts": self.artifacts,
            "pii_detected": self.pii_detected,
        }

        if self.classification:
            manifest["classification"] = self.classification

        return manifest

    def to_json(self, canonical: bool = True) -> str:
        """Convert manifest to JSON string (canonical if requested)."""
        data = self.to_dict()

        if canonical:
            # JCS (JSON Canonicalization Scheme) - sort keys, no whitespace
            return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)

    def add_artifact(
        self,
        artifact_type: str,
        path: str,
        hash_value: str,
        vault_ref: Optional[str] = None,
    ) -> None:
        """Add artifact to manifest."""
        artifact = {
            "type": artifact_type,
            "path": path,
            "hash": hash_value,
        }

        if vault_ref:
            artifact["vault_ref"] = vault_ref

        self.artifacts.append(artifact)


def create_manifest(
    case_id: str,
    url: str,
    base_path: Path,
    artifacts: List[Dict],
    classification: Optional[Dict] = None,
    pii_detected: bool = False,
) -> Manifest:
    """Create manifest from case data."""
    manifest = Manifest(
        case_id=case_id,
        url=url,
        artifacts=[],
        classification=classification,
        pii_detected=pii_detected,
    )

    for artifact in artifacts:
        artifact_path = base_path / artifact["path"]
        if artifact_path.exists():
            hash_value = hash_file(artifact_path)
            manifest.add_artifact(
                artifact_type=artifact["type"],
                path=artifact["path"],
                hash_value=hash_value,
                vault_ref=artifact.get("vault_ref"),
            )

    return manifest

