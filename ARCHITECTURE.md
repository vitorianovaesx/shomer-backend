# Shomer Backend Architecture

## Overview

Shomer backend is a content ingestion, classification, and case management system with GDPR-compliant PII handling, cryptographic integrity, and chain of custody.

## Core Components

### 1. Ingestion (`internal/ingest/`)
- **ContentFetcher**: Fetches content from URLs, extracts HTML, text, and images
- Uses `httpx` for async HTTP requests
- Uses `BeautifulSoup` for HTML parsing

### 2. PII Handling (`internal/pii/`)
- **PIIDetector**: Detects PII using Presidio (with regex fallback)
- **Pseudonymizer**: Deterministic pseudonymization using HMAC
- Ensures reproducibility: same input → same pseudonym

### 3. Storage (`internal/store/`)
- **CaseStore**: SQLite-based case and artifact storage
- **Vault**: Encrypted storage (Fernet) for PII and images
- Content-addressed paths for artifacts

### 4. Cryptography (`internal/crypto/`)
- **Hash**: SHA256 hashing for artifacts
- **Sign**: Ed25519 signing for manifests
- Canonical manifest in JCS (JSON Canonicalization Scheme) format

### 5. Classification (`internal/classify/`)
- **Classifier**: LLM-based antisemitism classifier integration
- Async HTTP client for ML service
- Graceful error handling when ML service unavailable

### 6. Pack Generation (`internal/pack/`)
- **Manifest**: Canonical JSON manifest with all artifacts
- **PackGenerator**: Creates ZIP files with:
  - manifest.json (canonical)
  - manifest.sig (Ed25519 signature)
  - pubkey.pem (public key for verification)
  - All artifacts
  - chain_of_custody.log

### 7. Chain of Custody (`internal/custody/`)
- **ChainOfCustodyLogger**: Append-only JSON-lines log
- No PII in logs (only references)
- Immutable audit trail

### 8. Pipeline (`internal/pipeline.py`)
- **IngestionPipeline**: Orchestrates the entire ingestion flow
- Handles errors gracefully with custody logging
- Ensures deterministic outputs for reproducibility

## Data Flow

```
URL → Fetch → Extract (HTML/Text/Images)
  ↓
PII Detection → Pseudonymize (if PII found)
  ↓
Store in Vault (if PII/images) → Store redacted in hot storage
  ↓
Hash artifacts → Classify (LLM) → Create manifest
  ↓
Sign manifest → Generate pack (ZIP)
  ↓
Chain of custody logging (all steps)
```

## API Endpoints

- `POST /ingest`: Ingest a URL, create case
- `GET /cases/{id}`: Get case details
- `GET /cases/{id}/pack.zip`: Download case pack
- `POST /cases/{id}/request_vault_access`: Request vault access (admin only)
- `GET /healthz`: Health check

## Security & Privacy

- **PII**: Detected, pseudonymized, originals moved to vault
- **Images**: Always moved to vault
- **Vault**: Encrypted with Fernet (prototype), LUKS/age in production
- **Signing**: Ed25519 signatures on canonical manifests
- **Hashing**: SHA256 for all artifacts
- **Logs**: No PII, only references

## Reproducibility

- Deterministic pseudonymization (HMAC with fixed key)
- Canonical manifest (JCS format)
- Content-addressed storage
- Re-ingesting same content → identical hashes and manifest bytes

## Testing

- Unit tests for all core components
- Integration tests for pipeline
- Test coverage ≥60% (target)
- Tests for deterministic pseudonymization
- Tests for hash/sign pipeline

## Future Work (Part B)

- Legal mapping module (`internal/map_law/`)
- Brief generation
- Dispatch system
- KPI instrumentation
- Pilot metrics


