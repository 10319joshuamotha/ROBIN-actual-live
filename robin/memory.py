from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from datetime import datetime, timezone


@dataclass(frozen=True)
class Memory:
    key: str
    value: str
    created_at: str


class MemoryStore:
    """Small local JSON memory store; encrypted storage will be added later."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def remember(self, key: str, value: str) -> Memory:
        memory = Memory(key, value, datetime.now(timezone.utc).isoformat())
        data = self._load()
        data.append(asdict(memory))
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return memory

    def search(self, query: str) -> list[Memory]:
        q = query.casefold()
        return [
            Memory(**item)
            for item in self._load()
            if q in item["key"].casefold() or q in item["value"].casefold()
        ]
