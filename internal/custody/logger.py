"""Chain of custody logger - append-only JSON-lines log."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class ChainOfCustodyLogger:
    """Append-only chain of custody logger."""

    def __init__(self, log_path: Path):
        """Initialize chain of custody logger."""
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        case_id: str,
        action: str,
        status: str = "success",
        actor: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log an event to chain of custody."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_id,
            "action": action,
            "status": status,
            "actor": actor,
            "metadata": metadata or {},
        }

        if error:
            entry["error"] = error

        # Ensure no PII in logs - metadata should not contain sensitive data
        log_line = json.dumps(entry, sort_keys=True)
        with open(self.log_path, "a") as f:
            f.write(log_line + "\n")

    def get_events(self, case_id: Optional[str] = None) -> list:
        """Get all events, optionally filtered by case_id."""
        events = []
        if not self.log_path.exists():
            return events

        with open(self.log_path, "r") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    if case_id is None or event.get("case_id") == case_id:
                        events.append(event)

        return events


