"""PII detection using Presidio."""

from typing import Dict, List

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False


class PIIDetector:
    """PII detector using Presidio."""

    def __init__(self, languages: List[str] = None):
        """Initialize PII detector."""
        self.languages = languages or ["en"]

        if not PRESIDIO_AVAILABLE:
            # Fallback: simple regex-based detection
            self._use_presidio = False
            self._init_regex_patterns()
        else:
            self._use_presidio = True
            try:
                # Initialize Presidio analyzer
                provider = NlpEngineProvider(conf_file=None)
                nlp_engine = provider.create_engine()
                self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=self.languages)
            except Exception:
                # Fallback to regex if Presidio fails
                self._use_presidio = False
                self._init_regex_patterns()

    def _init_regex_patterns(self):
        """Initialize regex patterns for basic PII detection."""
        import re

        # Basic patterns for common PII
        self.patterns = {
            "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "PHONE": re.compile(r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b'),
            "SSN": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "CREDIT_CARD": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
        }

    def detect(self, text: str) -> List[Dict]:
        """Detect PII in text."""
        if self._use_presidio:
            results = self.analyzer.analyze(text=text, language="en")
            return [
                {
                    "entity_type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                }
                for result in results
            ]
        else:
            # Use regex fallback
            detections = []
            for entity_type, pattern in self.patterns.items():
                for match in pattern.finditer(text):
                    detections.append(
                        {
                            "entity_type": entity_type,
                            "start": match.start(),
                            "end": match.end(),
                            "score": 0.8,  # Default score for regex
                        }
                    )
            return detections

    def has_pii(self, text: str) -> bool:
        """Check if text contains PII."""
        return len(self.detect(text)) > 0

