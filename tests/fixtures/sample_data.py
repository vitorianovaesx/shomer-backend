"""Sample test data for testing the ingestion pipeline."""

# Sample HTML content without PII
SAMPLE_HTML_NO_PII = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Article</title>
</head>
<body>
    <h1>Welcome to Our Website</h1>
    <p>This is a sample article with no personal information.</p>
    <p>It contains general information about our services.</p>
</body>
</html>
"""

# Sample HTML content with PII
SAMPLE_HTML_WITH_PII = """
<!DOCTYPE html>
<html>
<head>
    <title>Contact Us</title>
</head>
<body>
    <h1>Contact Information</h1>
    <p>Please contact John Doe at john.doe@example.com</p>
    <p>Or call us at 555-123-4567</p>
    <p>Our office is located at 123 Main St, Anytown, USA</p>
    <p>SSN: 123-45-6789</p>
</body>
</html>
"""

# Sample text content without PII
SAMPLE_TEXT_NO_PII = """
This is a sample text document without any personal information.
It contains general information about a topic.
No email addresses, phone numbers, or other PII are present.
"""

# Sample text content with PII
SAMPLE_TEXT_WITH_PII = """
Contact Information:
Name: Jane Smith
Email: jane.smith@example.com
Phone: (555) 987-6543
Address: 456 Oak Avenue, Springfield, IL 62701
SSN: 987-65-4321
Credit Card: 4532-1234-5678-9010
"""

# Sample text for classification testing (antisemitism-related content)
SAMPLE_TEXT_FOR_CLASSIFICATION = """
This is a sample text that may contain content for classification.
The ML classifier will analyze this text for antisemitism indicators.
"""

# Mock classifier response
MOCK_CLASSIFIER_RESPONSE = {
    "classification": "positive",
    "confidence": 0.85,
    "categories": ["hate_speech", "antisemitism"],
    "model_version": "v1.0",
    "timestamp": "2025-01-01T00:00:00Z"
}

# Sample URLs for testing
TEST_URLS = [
    "https://example.com",
    "https://example.org",
    "https://httpbin.org/html",  # Good for testing HTML parsing
    "https://httpbin.org/json",   # Good for testing JSON responses
]

# Sample image URLs (for testing image handling)
TEST_IMAGE_URLS = [
    "https://httpbin.org/image/png",
    "https://httpbin.org/image/jpeg",
]

