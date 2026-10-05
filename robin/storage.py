from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib


@dataclass(frozen=True)
class StorageLayout:
    local_root: Path
    usb_root: Path

    @property
    def local_master_metadata(self) -> Path:
        return self.local_root / "master-state.json"

    @property
    def usb_backup_manifest(self) -> Path:
        return self.usb_root / "backup-manifest.json"


class StorageManager:
    """Defines the local-runtime/USB-backup boundary.

    Encryption, integrity signing, and migration workflows are intentionally
    separate implementation milestones; this class does not claim to provide
    cryptographic protection yet.
    """

    def __init__(self, layout: StorageLayout) -> None:
        self.layout = layout

    @staticmethod
    def fingerprint(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def describe(self) -> dict[str, str]:
        return {
            "local_root": str(self.layout.local_root),
            "usb_root": str(self.layout.usb_root),
            "model": "local-runtime-plus-portable-master-backup",
        }
