"""LLM classifier integration for antisemitism detection."""

import json
from typing import Dict, Optional

import httpx


class Classifier:
    """LLM-based classifier integration."""

    def __init__(self, ml_endpoint: str, timeout: int = 30):
        """Initialize classifier."""
        self.ml_endpoint = ml_endpoint
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def classify(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """Classify text using LLM service."""
        try:
            payload = {
                "text": text,
                "metadata": metadata or {},
            }

            response = await self.client.post(
                self.ml_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            result = response.json()
            return {
                "classification": result.get("classification", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "categories": result.get("categories", []),
                "model_version": result.get("model_version", "unknown"),
                "timestamp": result.get("timestamp"),
            }
        except httpx.RequestError as e:
            # If ML service is unavailable, return default classification
            return {
                "classification": "error",
                "confidence": 0.0,
                "categories": [],
                "model_version": "unknown",
                "error": str(e),
            }
        except Exception as e:
            return {
                "classification": "error",
                "confidence": 0.0,
                "categories": [],
                "model_version": "unknown",
                "error": str(e),
            }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()



