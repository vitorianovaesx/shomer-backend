"""Main ingestion pipeline."""

import asyncio
from pathlib import Path
from typing import Dict, Optional

from internal.classify.classifier import Classifier
from internal.config import Config
from internal.custody.logger import ChainOfCustodyLogger
from internal.ingest.fetcher import ContentFetcher
from internal.pack.manifest import Manifest
from internal.pack.packer import PackGenerator
from internal.pii.detector import PIIDetector
from internal.pii.pseudonymizer import Pseudonymizer
from internal.store.case_store import CaseStore
from internal.store.vault import Vault
from internal.crypto.hash import compute_sha256, hash_file


class IngestionPipeline:
    """Main ingestion pipeline."""

    def __init__(self, config: Config):
        """Initialize pipeline."""
        self.config = config
        self.case_store = CaseStore(Path(config.storage.sqlite_path))
        self.vault = Vault(Path(config.storage.vault_path))
        self.custody_logger = ChainOfCustodyLogger(
            Path(config.storage.base_path) / "chain_of_custody.log"
        )
        self.fetcher = ContentFetcher(timeout=30)
        self.pii_detector = PIIDetector(languages=config.pii.languages)
        self.pseudonymizer = Pseudonymizer(config.pii.hmac_key)
        self.classifier = Classifier(
            config.classify.ml_endpoint, timeout=config.classify.timeout
        )
        self.pack_generator = PackGenerator(
            Path(config.storage.base_path),
            Path(config.crypto.key_path),
            config.crypto.key_name,
        )
        self.base_path = Path(config.storage.base_path)

    async def ingest(self, url: str) -> str:
        """Ingest URL and return case_id."""
        # Create case
        case_id = self.case_store.create_case(url)
        self.custody_logger.log(case_id, "created", actor="system", metadata={"url": url})

        try:
            # Fetch content
            self.custody_logger.log(case_id, "fetched", status="in_progress")
            content = await self.fetcher.fetch(url)
            self.custody_logger.log(case_id, "fetched", status="success")

            # Create case directory
            case_dir = self.base_path / case_id
            case_dir.mkdir(parents=True, exist_ok=True)

            artifacts = []
            pii_detected = False

            # Process text
            text_content = content.get("text", "")
            text_detections = self.pii_detector.detect(text_content)
            redacted_text = None

            if text_detections:
                pii_detected = True
                self.custody_logger.log(
                    case_id,
                    "pii-detected",
                    metadata={"count": len(text_detections)},
                )

                # Store original text in vault
                original_text_bytes = text_content.encode("utf-8")
                vault_ref = self.vault.store(
                    original_text_bytes,
                    metadata={"type": "text", "url": url, "case_id": case_id},
                )
                self.custody_logger.log(
                    case_id,
                    "pii-moved",
                    metadata={"vault_ref": vault_ref, "type": "text"},
                )

                # Pseudonymize text
                redacted_text = self.pseudonymizer.pseudonymize_text(
                    text_content, text_detections
                )
                self.custody_logger.log(case_id, "pseudonymized", metadata={"type": "text"})

                # Save redacted text
                redacted_path = case_dir / "text_redacted.txt"
                redacted_path.write_text(redacted_text, encoding="utf-8")
                artifacts.append(
                    {
                        "type": "text_redacted",
                        "path": f"{case_id}/text_redacted.txt",
                        "vault_ref": vault_ref,
                    }
                )
                self.case_store.add_artifact(
                    case_id, "text_redacted", redacted_path, vault_ref=vault_ref
                )
            else:
                # No PII, save text directly
                text_path = case_dir / "text.txt"
                text_path.write_text(text_content, encoding="utf-8")
                artifacts.append(
                    {"type": "text", "path": f"{case_id}/text.txt"}
                )
                self.case_store.add_artifact(case_id, "text", text_path)

            # Process HTML (always save, may contain PII)
            html_content = content.get("html", "")
            html_detections = self.pii_detector.detect(html_content)

            if html_detections:
                pii_detected = True
                # Store original HTML in vault
                original_html_bytes = html_content.encode("utf-8")
                vault_ref = self.vault.store(
                    original_html_bytes,
                    metadata={"type": "html", "url": url, "case_id": case_id},
                )
                self.custody_logger.log(
                    case_id,
                    "pii-moved",
                    metadata={"vault_ref": vault_ref, "type": "html"},
                )

                # Pseudonymize HTML
                redacted_html = self.pseudonymizer.pseudonymize_text(
                    html_content, html_detections
                )
                redacted_html_path = case_dir / "html_redacted.html"
                redacted_html_path.write_text(redacted_html, encoding="utf-8")
                artifacts.append(
                    {
                        "type": "html_redacted",
                        "path": f"{case_id}/html_redacted.html",
                        "vault_ref": vault_ref,
                    }
                )
                self.case_store.add_artifact(
                    case_id, "html_redacted", redacted_html_path, vault_ref=vault_ref
                )
            else:
                html_path = case_dir / "html.html"
                html_path.write_text(html_content, encoding="utf-8")
                artifacts.append(
                    {"type": "html", "path": f"{case_id}/html.html"}
                )
                self.case_store.add_artifact(case_id, "html", html_path)

            # Process images - always move to vault
            images = content.get("images", [])
            for img_url in images[:10]:  # Limit to first 10 images
                try:
                    img_data = await self.fetcher.fetch_image(img_url)
                    vault_ref = self.vault.store(
                        img_data,
                        metadata={
                            "type": "image",
                            "url": img_url,
                            "case_id": case_id,
                        },
                    )
                    self.custody_logger.log(
                        case_id,
                        "image-moved",
                        metadata={"vault_ref": vault_ref, "image_url": img_url},
                    )
                except Exception as e:
                    self.custody_logger.log(
                        case_id,
                        "image-fetch-failed",
                        status="error",
                        error=str(e),
                        metadata={"image_url": img_url},
                    )

            # Hash artifacts
            self.custody_logger.log(case_id, "hashed", status="in_progress")
            for artifact in artifacts:
                artifact_path = self.base_path / artifact["path"]
                if artifact_path.exists():
                    hash_value = hash_file(artifact_path)
                    artifact["hash"] = hash_value
            self.custody_logger.log(case_id, "hashed", status="success")

            # Classify text
            text_to_classify = redacted_text if redacted_text else text_content
            self.custody_logger.log(case_id, "classified", status="in_progress")
            classification = await self.classifier.classify(
                text_to_classify, metadata={"url": url, "case_id": case_id}
            )
            self.custody_logger.log(
                case_id,
                "classified",
                status="success",
                metadata={"classification": classification.get("classification")},
            )

            # Create manifest
            manifest = Manifest(
                case_id=case_id,
                url=url,
                artifacts=artifacts,
                classification=classification,
                pii_detected=pii_detected,
            )

            # Sign manifest
            manifest_json = manifest.to_json(canonical=True)
            manifest_hash = compute_sha256(manifest_json.encode("utf-8"))
            self.custody_logger.log(case_id, "signed", metadata={"manifest_hash": manifest_hash})

            # Generate pack
            artifact_paths = [
                self.base_path / artifact["path"] for artifact in artifacts
            ]
            chain_of_custody_path = Path(self.config.storage.base_path) / "chain_of_custody.log"
            pack_path = self.pack_generator.create_pack(
                case_id, manifest, artifact_paths, chain_of_custody_path
            )
            self.custody_logger.log(
                case_id,
                "packaged",
                metadata={"pack_path": str(pack_path)},
            )

            # Update case status
            self.case_store.update_case_status(
                case_id, "completed", manifest_hash=manifest_hash, pack_path=str(pack_path)
            )

            return case_id

        except Exception as e:
            self.custody_logger.log(
                case_id,
                "ingest-failed",
                status="error",
                error=str(e),
            )
            self.case_store.update_case_status(case_id, "failed")
            raise

    async def close(self):
        """Close resources."""
        await self.fetcher.close()
        await self.classifier.close()

