"""Deterministic pseudonymization using HMAC."""

import hashlib
import hmac
from typing import Optional


class Pseudonymizer:
    """Deterministic pseudonymizer using HMAC."""

    def __init__(self, hmac_key: str):
        """Initialize pseudonymizer with HMAC key."""
        if not hmac_key:
            raise ValueError("HMAC key is required for deterministic pseudonymization")
        self.hmac_key = hmac_key.encode() if isinstance(hmac_key, str) else hmac_key

    def pseudonymize(self, text: str, entity_type: Optional[str] = None) -> str:
        """Pseudonymize a value deterministically."""
        # Create HMAC hash
        key = f"{entity_type}:{text}" if entity_type else text
        hmac_hash = hmac.new(
            self.hmac_key,
            key.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # Use first 8 characters as pseudonym
        prefix = entity_type[:3].upper() if entity_type else "VAL"
        return f"[{prefix}_{hmac_hash[:8]}]"

    def pseudonymize_text(self, text: str, detections: list) -> str:
        """Pseudonymize PII in text based on detections."""
        # Sort detections by start position (reverse to avoid index shifting)
        sorted_detections = sorted(detections, key=lambda x: x["start"], reverse=True)

        result = text
        for detection in sorted_detections:
            start = detection["start"]
            end = detection["end"]
            original = text[start:end]
            entity_type = detection.get("entity_type", "UNKNOWN")
            pseudonym = self.pseudonymize(original, entity_type)
            result = result[:start] + pseudonym + result[end:]

        return result



