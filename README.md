# Shomer Backend

Content ingestion, classification, and case management system with GDPR-compliant PII handling, cryptographic integrity, and chain of custody.

## Architecture

- **Ingestion**: Static seed list → content capture (HTML, text, images)
- **PII Handling**: Detection, pseudonymization, vault storage
- **Integrity**: SHA256 hashing, Ed25519 signing
- **Classification**: LLM-based antisemitism classifier integration
- **Storage**: SQLite + local FS (content-addressed), encrypted vault
- **Chain of Custody**: Append-only JSON-lines log

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and set SHOMER_HMAC_KEY and SHOMER_ADMIN_TOKEN
# Generate keys:
#   python -c "import secrets; print('SHOMER_HMAC_KEY=' + secrets.token_hex(32))"
#   python -c "import secrets; print('SHOMER_ADMIN_TOKEN=' + secrets.token_urlsafe(32))"

# Update seed URLs in config.yaml (optional)
python scripts/seed_urls.py

# Run the API server
python -m cmd.shomer serve
# Or use Makefile:
# make serve
```

### Usage

```bash
# Ingest a URL
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Get case details
curl http://localhost:8000/cases/{case_id}

# Get case pack (ZIP file)
curl http://localhost:8000/cases/{case_id}/pack.zip -o pack.zip

# Request vault access (requires admin token)
curl -X POST http://localhost:8000/cases/{case_id}/request_vault_access \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### CLI Usage

```bash
# Ingest via CLI
python -m cmd.shomer ingest https://example.com
```

## Project Structure

```
shomer-backend/
├── internal/
│   ├── ingest/      # URL fetching, content extraction
│   ├── pii/         # PII detection and pseudonymization
│   ├── classify/    # LLM classifier integration
│   ├── pack/        # Pack generation (ZIP, manifest, signatures)
│   ├── store/       # Storage (SQLite, FS, vault)
│   └── crypto/      # Hashing, signing
├── api/             # FastAPI endpoints
├── cmd/             # CLI commands
├── tests/           # Unit and integration tests
└── scripts/         # Utility scripts
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=internal --cov=api --cov=cmd --cov-report=html

# Format code
black .
ruff check --fix .
```

## License

MIT License

