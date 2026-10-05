from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import RobinConfig
from .storage import StorageManager


@dataclass(frozen=True)
class HealthReport:
    config_ok: bool
    data_path: bool
    log_path: bool
    usb_path: bool
    storage_model: str

    @property
    def ok(self) -> bool:
        return self.config_ok and self.data_path and self.log_path


def check_health(config: RobinConfig) -> HealthReport:
    config.ensure_directories()
    paths = config.paths
    return HealthReport(
        config_ok=True,
        data_path=Path(paths.data).is_dir(),
        log_path=Path(paths.logs).is_dir(),
        usb_path=bool(paths.usb and paths.usb.is_dir() and StorageManager.is_removable_drive(paths.usb)),
        storage_model="local-first-with-encrypted-removable-backup",
    )
