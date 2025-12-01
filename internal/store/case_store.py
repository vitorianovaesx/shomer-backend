"""SQLite-based case storage."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from internal.crypto.hash import compute_sha256


class CaseStore:
    """Case storage using SQLite."""

    def __init__(self, db_path: Path):
        """Initialize case store."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    manifest_hash TEXT,
                    pack_path TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    vault_ref TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id)
                )
            """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_artifacts_case_id 
                ON artifacts(case_id)
            """
            )
            conn.commit()

    def create_case(self, url: str) -> str:
        """Create a new case and return case_id."""
        case_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO cases (case_id, url, created_at, status)
                VALUES (?, ?, ?, ?)
            """,
                (case_id, url, now, "created"),
            )
            conn.commit()

        return case_id

    def get_case(self, case_id: str) -> Optional[Dict]:
        """Get case by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM cases WHERE case_id = ?", (case_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def update_case_status(
        self, case_id: str, status: str, manifest_hash: Optional[str] = None, pack_path: Optional[str] = None
    ) -> None:
        """Update case status."""
        updates = ["status = ?"]
        params = [status]

        if manifest_hash:
            updates.append("manifest_hash = ?")
            params.append(manifest_hash)

        if pack_path:
            updates.append("pack_path = ?")
            params.append(pack_path)

        params.append(case_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"UPDATE cases SET {', '.join(updates)} WHERE case_id = ?",
                params,
            )
            conn.commit()

    def add_artifact(
        self,
        case_id: str,
        artifact_type: str,
        path: Path,
        content: Optional[bytes] = None,
        vault_ref: Optional[str] = None,
    ) -> str:
        """Add artifact to case."""
        artifact_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        if content is None:
            content = path.read_bytes()

        artifact_hash = compute_sha256(content)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO artifacts 
                (artifact_id, case_id, artifact_type, path, hash, vault_ref, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    artifact_id,
                    case_id,
                    artifact_type,
                    str(path),
                    artifact_hash,
                    vault_ref,
                    now,
                ),
            )
            conn.commit()

        return artifact_id

    def get_artifacts(self, case_id: str) -> List[Dict]:
        """Get all artifacts for a case."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM artifacts WHERE case_id = ? ORDER BY created_at",
                (case_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

