# Implementation Status

## Sprint 0 - Core Infrastructure ✅

### Completed Components

1. **Project Structure** ✅
   - Complete directory layout (`/internal`, `/api`, `/cmd`, `/tests`, `/scripts`)
   - Dependencies configured (`requirements.txt`, `pyproject.toml`)
   - CI/CD setup (`.github/workflows/ci.yml`)

2. **Cryptographic Infrastructure** ✅
   - SHA256 hashing (`internal/crypto/hash.py`)
   - Ed25519 signing (`internal/crypto/sign.py`)
   - Keypair generation and persistence
   - Canonical manifest generation (JCS format)

3. **Storage Layer** ✅
   - SQLite case store (`internal/store/case_store.py`)
   - Encrypted vault (Fernet) for PII and images (`internal/store/vault.py`)
   - Content-addressed artifact storage

4. **Ingestion Pipeline** ✅
   - URL fetching with `httpx` (`internal/ingest/fetcher.py`)
   - HTML parsing and text extraction
   - Image extraction and handling

5. **PII Handling** ✅
   - PII detection using Presidio (with regex fallback)
   - Deterministic pseudonymization (HMAC-based)
   - Vault integration for PII originals

6. **Chain of Custody** ✅
   - Append-only JSON-lines logging
   - No PII in logs (only references)
   - Immutable audit trail

7. **Pack Generation** ✅
   - ZIP file creation with all artifacts
   - Manifest, signature, and public key inclusion
   - Chain of custody log in pack

8. **API Endpoints** ✅
   - `POST /ingest` - Ingest URL
   - `GET /cases/{id}` - Get case details
   - `GET /cases/{id}/pack.zip` - Download pack
   - `POST /cases/{id}/request_vault_access` - Vault access (admin)
   - `GET /healthz` - Health check

9. **Classification Integration** ✅
   - LLM classifier interface (`internal/classify/classifier.py`)
   - Async HTTP client for ML service
   - Error handling for unavailable services

10. **Testing** ✅
    - Unit tests for all core components
    - Tests for deterministic pseudonymization
    - Tests for hash/sign pipeline
    - Integration test structure
    - Coverage target: ≥60%

## Sprint 1 - PII Handling + Chain of Custody ✅

All Sprint 1 requirements are integrated into Sprint 0:
- ✅ Text PII scanner + pseudonymizer
- ✅ Auto move-to-Vault for PII and images
- ✅ Append-only chain_of_custody.log
- ✅ Deterministic HMAC tokens for reproducibility

## Sprint 2 - LLM Integration ✅

- ✅ Backend interfaces for `/internal/classify`
- ✅ Input/output schemas (JSON contracts)
- ✅ Async execution and error handling
- ✅ Manifest update and chain-of-custody logging
- ✅ Unit tests with stubbed ML responses

## Acceptance Criteria

### Reproducibility ✅
- Re-ingesting unchanged content → identical hashes
- Identical manifest bytes (deterministic pseudonymization)
- HMAC-based pseudonymization ensures consistency

### Completeness ✅
- Pack contains:
  - Raw/redacted artifacts
  - Derived classification
  - Manifest (canonical JSON)
  - Signature (Ed25519)
  - Public key
  - Chain of custody log

### Integrity ✅
- SHA256 checksums in manifest
- Ed25519 signature verification
- Public key included in pack

### Reliability ✅
- Errors logged in chain_of_custody
- Graceful error handling
- Status tracking in case store

### Documentation & CI ✅
- README with setup instructions
- Architecture documentation
- CI configuration (GitHub Actions)
- Test coverage structure

## Next Steps (Part B)

1. **Legal Mapping Module** (`internal/map_law/`)
   - Map classification to local law
   - Generate briefs
   - Dispatch system

2. **KPI Instrumentation**
   - Metrics collection
   - Pilot KPIs
   - Dashboard/export

3. **Production Hardening**
   - LUKS/age encryption for vault
   - S3 adapter for hot storage
   - Auth/RBAC for multitenancy
   - Cloud deployment

## Known Limitations (Per Spec)

- ✅ No auth/RBAC/multitenancy (except admin token for vault)
- ✅ No cloud hardening (local FS + SQLite)
- ✅ Images not classified (moved to vault)
- ✅ Vault as local encrypted directory (Fernet)
- ✅ Minimal UI (CLI + API)

## Configuration

- `config.yaml`: Main configuration file
- `.env`: Environment variables (HMAC key, admin token)
- Seed URLs: Configured in `config.yaml` (15-20 URLs)

## Usage

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with SHOMER_HMAC_KEY and SHOMER_ADMIN_TOKEN

# Run
python -m cmd.shomer serve

# Test
pytest --cov
```

