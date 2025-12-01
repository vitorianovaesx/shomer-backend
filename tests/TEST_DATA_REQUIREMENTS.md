# Test Data Requirements

This document outlines what test data is needed to properly test the Shomer backend system.

## Required Test Data

### 1. Sample URLs for Ingestion Testing

**Purpose:** Test the URL fetching and content extraction pipeline

**Required:**
- Public URLs that return HTML content
- URLs that are safe to fetch (no authentication required)
- URLs that won't change frequently (for reproducible tests)

**Examples:**
- `https://example.com` - Simple HTML page
- `https://httpbin.org/html` - Test HTML parsing
- `https://httpbin.org/json` - Test JSON handling

**Location:** `tests/fixtures/sample_data.py` → `TEST_URLS`

### 2. Sample HTML Content

**Purpose:** Test HTML parsing, text extraction, and PII detection

**Required:**
- HTML with PII (emails, phones, SSN, credit cards)
- HTML without PII (clean content)
- HTML with images (for image extraction testing)

**Location:** `tests/fixtures/sample_data.py` → `SAMPLE_HTML_*`

### 3. Sample Text Content

**Purpose:** Test PII detection and pseudonymization

**Required:**
- Text with various PII types:
  - Email addresses
  - Phone numbers
  - Social Security Numbers (SSN)
  - Credit card numbers
  - Names and addresses
- Text without PII (for negative testing)

**Location:** `tests/fixtures/sample_data.py` → `SAMPLE_TEXT_*`

### 4. Sample Images

**Purpose:** Test image handling and vault storage

**Required:**
- Small test images (PNG, JPEG)
- Images that can be fetched via URL
- Images for testing vault storage

**Location:** `tests/fixtures/sample_data.py` → `TEST_IMAGE_URLS`

### 5. Mock Classifier Responses

**Purpose:** Test LLM classifier integration

**Required:**
- Mock responses for classification API
- Different classification results (positive, negative, error)
- Confidence scores and categories

**Location:** `tests/fixtures/sample_data.py` → `MOCK_CLASSIFIER_RESPONSE`

### 6. Configuration Data

**Purpose:** Test configuration loading and validation

**Required:**
- Valid configuration files
- Invalid configuration files (for error testing)
- Environment variables:
  - `SHOMER_HMAC_KEY` - For deterministic pseudonymization
  - `SHOMER_ADMIN_TOKEN` - For admin operations

**Location:** `config.yaml`, `.env.example`

## Test Data Structure

```
tests/
├── fixtures/
│   ├── __init__.py
│   ├── sample_data.py      # Sample content (HTML, text, URLs)
│   └── mock_responses.py   # Mock HTTP responses
├── data/                   # Optional: static test files
│   ├── sample.html
│   ├── sample.txt
│   └── test_image.png
└── conftest.py            # Pytest fixtures
```

## Usage in Tests

### Example: Using Sample Data

```python
from tests.fixtures.sample_data import (
    SAMPLE_HTML_WITH_PII,
    SAMPLE_TEXT_WITH_PII,
    MOCK_CLASSIFIER_RESPONSE
)

def test_pii_detection():
    detector = PIIDetector()
    detections = detector.detect(SAMPLE_TEXT_WITH_PII)
    assert len(detections) > 0
```

### Example: Mocking HTTP Responses

```python
from unittest.mock import patch
from tests.fixtures.mock_responses import create_mock_html_response
from tests.fixtures.sample_data import SAMPLE_HTML_NO_PII

@patch('httpx.AsyncClient.get')
async def test_fetch_content(mock_get):
    mock_get.return_value = create_mock_html_response(SAMPLE_HTML_NO_PII)
    # Test fetching...
```

## CI/CD Test Data

For CI/CD, we use:
- Environment variables set in `.github/workflows/ci.yml`
- Mock responses instead of real HTTP calls
- Temporary directories for storage
- Deterministic test data for reproducibility

## Privacy Considerations

⚠️ **Important:** Test data should NOT contain real PII:
- Use fake emails (e.g., `test@example.com`)
- Use fake phone numbers (e.g., `555-123-4567`)
- Use fake SSNs (e.g., `123-45-6789`)
- Never commit real personal information

## Adding New Test Data

1. Add sample content to `tests/fixtures/sample_data.py`
2. Create mock responses in `tests/fixtures/mock_responses.py` if needed
3. Update this document with new requirements
4. Ensure test data is deterministic and reproducible

