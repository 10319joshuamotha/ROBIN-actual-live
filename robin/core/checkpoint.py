from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Checkpoint:
    identifier: str
    created_at: str
    description: str
    path: Path


class CheckpointStore:
    """Local checkpoint contract used before upgrades can be activated."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def create(self, description: str) -> Checkpoint:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        identifier = f"checkpoint-{timestamp}"
        path = self.root / identifier
        path.mkdir(parents=True, exist_ok=False)
        (path / "description.txt").write_text(description, encoding="utf-8")
        return Checkpoint(identifier, timestamp, description, path)
