from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

from .crypto import decrypt_bytes, encrypt_bytes, write_atomic


@dataclass(frozen=True)
class Memory:
    key: str
    value: str
    created_at: str


class MemoryStore:
    """Local encrypted memory; the passphrase is supplied by the caller, never saved."""

    def __init__(self, path: Path, passphrase: str) -> None:
        self.path = Path(path)
        self.passphrase = passphrase

    def _load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        raw = decrypt_bytes(self.path.read_bytes(), self.passphrase)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Encrypted memory payload is not valid JSON.") from None
        expected = {"key", "value", "created_at"}
        if not isinstance(data, list) or any(
            not isinstance(item, dict)
            or set(item) != expected
            or not all(isinstance(item.get(field), str) for field in expected)
            for item in data
        ):
            raise ValueError("Encrypted memory payload has an unsupported structure.")
        return data

    def remember(self, key: str, value: str) -> Memory:
        if not key.strip():
            raise ValueError("Memory key cannot be empty.")
        memory = Memory(key, value, datetime.now(timezone.utc).isoformat())
        data = self._load()
        data.append(asdict(memory))
        encrypted = encrypt_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"), self.passphrase)
        write_atomic(self.path, encrypted)
        return memory

    def search(self, query: str) -> list[Memory]:
        q = query.casefold()
        return [
            Memory(**item)
            for item in self._load()
            if q in item["key"].casefold() or q in item["value"].casefold()
        ]
