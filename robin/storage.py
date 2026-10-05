from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import stat
import tempfile
from typing import Callable

from .crypto import decrypt_bytes, encrypt_bytes, write_atomic


_MAX_FILE_COUNT = 10_000
_MAX_TOTAL_FILE_BYTES = 48 * 1024 * 1024
_MAX_ENCRYPTED_BACKUP_BYTES = 64 * 1024 * 1024
_BACKUP_FORMAT = "robin-encrypted-backup-v1"


class BackupError(ValueError):
    """Raised when a backup cannot be safely created or restored."""


@dataclass(frozen=True)
class StorageLayout:
    local_root: Path
    usb_root: Path | None

    @property
    def local_master_metadata(self) -> Path:
        return self.local_root / "master-state.json"

    @property
    def usb_backup_manifest(self) -> Path | None:
        return self.usb_root / "backup-manifest.json" if self.usb_root else None


@dataclass(frozen=True)
class BackupResult:
    path: Path
    file_count: int
    encrypted_size: int
    fingerprint: str


class StorageManager:
    """Local-first storage with encrypted backups to verified removable drives."""

    def __init__(
        self,
        layout: StorageLayout,
        removable_drive_check: Callable[[Path], bool] | None = None,
    ) -> None:
        self.layout = layout
        self._removable_drive_check = removable_drive_check or self.is_removable_drive

    @staticmethod
    def is_removable_drive(path: Path | str) -> bool:
        if os.name != "nt":
            return False
        try:
            import ctypes

            candidate = Path(path)
            drive = candidate.resolve(strict=False).drive or candidate.drive
            if not drive:
                return False
            root = f"{drive}{chr(92)}"
            get_drive_type = ctypes.windll.kernel32.GetDriveTypeW
            get_drive_type.argtypes = [ctypes.c_wchar_p]
            get_drive_type.restype = ctypes.c_uint
            return get_drive_type(root) == 2
        except (AttributeError, OSError, ValueError):
            return False

    @staticmethod
    def fingerprint(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def describe(self) -> dict[str, str | None]:
        return {
            "local_root": str(self.layout.local_root),
            "usb_root": str(self.layout.usb_root) if self.layout.usb_root else None,
            "model": "local-first-with-encrypted-removable-backup",
        }

    @staticmethod
    def _safe_relative_path(name: str) -> Path:
        if not name or chr(92) in name:
            raise BackupError("Backup contains an unsafe file path.")
        relative = PurePosixPath(name)
        if relative.is_absolute() or any(part in ("", ".", "..") or ":" in part for part in relative.parts):
            raise BackupError("Backup contains an unsafe file path.")
        return Path(*relative.parts)

    def create_backup(
        self,
        passphrase: str,
        *,
        destination_root: Path | str | None = None,
        source_root: Path | str | None = None,
    ) -> BackupResult:
        source = Path(source_root) if source_root is not None else Path(self.layout.local_root)
        destination = Path(destination_root) if destination_root is not None else self.layout.usb_root
        if destination is None:
            raise BackupError("No USB backup destination is configured.")
        if not self._removable_drive_check(destination):
            raise BackupError("Backup destination is not a detected removable drive.")
        if not destination.is_dir():
            raise BackupError("USB destination is unavailable; no local substitute was created.")
        if not source.is_dir():
            raise BackupError("Local data directory does not exist.")
        source_resolved = source.resolve()
        destination_resolved = destination.resolve()
        if source_resolved == destination_resolved or source_resolved in destination_resolved.parents or destination_resolved in source_resolved.parents:
            raise BackupError("Backup source and destination must be separate directories.")

        files: list[dict[str, object]] = []
        total_bytes = 0
        for item in sorted(source.rglob("*")):
            info = item.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise BackupError("Local data contains a symbolic link; backup stopped.")
            if stat.S_ISDIR(info.st_mode):
                continue
            if not stat.S_ISREG(info.st_mode):
                raise BackupError("Local data contains an unsupported file type.")
            relative = item.relative_to(source).as_posix()
            self._safe_relative_path(relative)
            total_bytes += info.st_size
            if total_bytes > _MAX_TOTAL_FILE_BYTES or len(files) >= _MAX_FILE_COUNT:
                raise BackupError("Local data exceeds the safe backup size or file-count limit.")
            content = item.read_bytes()
            if len(content) != info.st_size:
                raise BackupError("A local file changed while the backup was being prepared.")
            files.append({
                "path": relative,
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "content": base64.b64encode(content).decode("ascii"),
            })

        payload = json.dumps(
            {"format": _BACKUP_FORMAT, "created_at": datetime.now(timezone.utc).isoformat(), "files": files},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(payload) > _MAX_ENCRYPTED_BACKUP_BYTES:
            raise BackupError("Backup payload exceeds the safe size limit.")
        encrypted = encrypt_bytes(payload, passphrase)
        if len(encrypted) > _MAX_ENCRYPTED_BACKUP_BYTES:
            raise BackupError("Encrypted backup exceeds the safe size limit.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = destination / f"robin-backup-{timestamp}-{secrets.token_hex(4)}.rbk"
        write_atomic(backup_path, encrypted)
        return BackupResult(backup_path, len(files), len(encrypted), self.fingerprint(encrypted))

    def restore_backup(
        self,
        backup_path: Path | str,
        destination: Path | str,
        passphrase: str,
    ) -> Path:
        backup = Path(backup_path)
        target = Path(destination)
        if not self._removable_drive_check(backup.parent):
            raise BackupError("Backup source is not on a detected removable drive.")
        if backup.is_symlink() or not backup.is_file():
            raise BackupError("Backup file is unavailable or is a symbolic link.")
        if backup.stat().st_size > _MAX_ENCRYPTED_BACKUP_BYTES:
            raise BackupError("Backup file exceeds the safe size limit.")
        if target.exists() or target.is_symlink():
            raise BackupError("Restore destination already exists; existing data was not changed.")

        try:
            payload = decrypt_bytes(backup.read_bytes(), passphrase)
            document = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise BackupError("Decrypted backup does not contain a valid ROBIN manifest.") from None
        if not isinstance(document, dict) or document.get("format") != _BACKUP_FORMAT or not isinstance(document.get("files"), list):
            raise BackupError("Backup format is unsupported.")

        entries: dict[str, bytes] = {}
        total_bytes = 0
        if len(document["files"]) > _MAX_FILE_COUNT:
            raise BackupError("Backup contains too many files.")
        for entry in document["files"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                raise BackupError("Backup manifest entry is invalid.")
            relative = self._safe_relative_path(entry["path"])
            key = relative.as_posix()
            if key in entries:
                raise BackupError("Backup contains duplicate file paths.")
            try:
                content = base64.b64decode(entry["content"], validate=True)
            except (KeyError, TypeError, ValueError):
                raise BackupError("Backup file data is invalid.") from None
            expected_size = entry.get("size")
            expected_hash = entry.get("sha256")
            if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size != len(content):
                raise BackupError("Backup file size does not match its manifest.")
            if not isinstance(expected_hash, str) or not secrets.compare_digest(hashlib.sha256(content).hexdigest(), expected_hash):
                raise BackupError("Backup file integrity check failed.")
            total_bytes += len(content)
            if total_bytes > _MAX_TOTAL_FILE_BYTES:
                raise BackupError("Backup contents exceed the safe size limit.")
            entries[key] = content

        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".robin-restore-", dir=target.parent))
        try:
            for name, content in entries.items():
                relative = self._safe_relative_path(name)
                output = stage / relative
                output.parent.mkdir(parents=True, exist_ok=True)
                if not output.resolve(strict=False).is_relative_to(stage.resolve()):
                    raise BackupError("Backup path escaped the restore directory.")
                write_atomic(output, content)
            os.replace(stage, target)
        except Exception:
            import shutil

            shutil.rmtree(stage, ignore_errors=True)
            raise
        return target
