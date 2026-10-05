from __future__ import annotations

from dataclasses import dataclass

from ..config import RobinConfig
from ..storage import StorageManager


@dataclass(frozen=True)
class HealthStatus:
    config: bool
    data: bool
    logs: bool
    usb: bool

    @property
    def ok(self) -> bool:
        return self.config and self.data and self.logs


def check(config: RobinConfig) -> HealthStatus:
    config.ensure_directories()
    p = config.paths
    return HealthStatus(
        config=True,
        data=p.data.is_dir(),
        logs=p.logs.is_dir(),
        usb=bool(p.usb and p.usb.is_dir() and StorageManager.is_removable_drive(p.usb)),
    )
