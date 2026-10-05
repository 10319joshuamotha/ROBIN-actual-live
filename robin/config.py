from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass(frozen=True)
class RobinPaths:
    root: Path
    data: Path
    logs: Path
    usb: Path | None

    @classmethod
    def from_environment(cls) -> "RobinPaths":
        root = Path(os.environ.get("ROBIN_ROOT", Path.home() / ".robin"))
        usb_value = os.environ.get("ROBIN_USB_PATH", "").strip()
        return cls(
            root=root,
            data=root / "data",
            logs=root / "logs",
            usb=Path(usb_value) if usb_value else None,
        )


@dataclass(frozen=True)
class RobinConfig:
    name: str = "ROBIN"
    version: str = "0.1.0"
    max_reminder_calls: int = 10
    sleep_wake_key: str = "ESC"
    local_first: bool = True
    paths: RobinPaths = field(default_factory=RobinPaths.from_environment)

    def ensure_directories(self) -> None:
        for path in (self.paths.root, self.paths.data, self.paths.logs):
            path.mkdir(parents=True, exist_ok=True)
