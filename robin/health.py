from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import RobinConfig
from .storage import StorageLayout, StorageManager


@dataclass(frozen=True)
class HealthReport:
    config_ok: bool
    data_path: bool
    log_path: bool
    usb_path: bool
    storage_model: str

    @property
    def ok(self) -> bool:
        return all((self.config_ok, self.data_path, self.log_path, self.usb_path))


def check_health(config: RobinConfig) -> HealthReport:
    paths = config.paths
    layout = StorageLayout(paths.data, paths.usb)
    StorageManager(layout)
    return HealthReport(
        config_ok=True,
        data_path=Path(paths.data).is_dir(),
        log_path=Path(paths.logs).is_dir(),
        usb_path=Path(paths.usb).is_dir(),
        storage_model="local-runtime-plus-portable-master-backup",
    )
