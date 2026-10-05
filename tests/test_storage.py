import base64
import hashlib
import json
from pathlib import Path

from robin.crypto import ENVELOPE_MAGIC, encrypt_bytes
from robin.storage import BackupError, StorageLayout, StorageManager


PASSPHRASE = "a stronger backup passphrase"


def _manager(local: Path, usb: Path) -> StorageManager:
    return StorageManager(
        StorageLayout(local, usb),
        removable_drive_check=lambda path: Path(path).resolve() == usb.resolve(),
    )


def _expect_error(expected, callback) -> None:
    try:
        callback()
    except expected:
        return
    raise AssertionError(f"Expected {expected.__name__}")


def test_backup_and_restore_round_trip_without_overwriting_local_data(tmp_path) -> None:
    local = tmp_path / "local-data"
    usb = tmp_path / "usb"
    local.mkdir()
    usb.mkdir()
    (local / "knowledge.txt").write_text("private knowledge", encoding="utf-8")
    manager = _manager(local, usb)

    created = manager.create_backup(PASSPHRASE)
    assert created.path.parent == usb
    assert created.path.read_bytes().startswith(ENVELOPE_MAGIC)
    assert b"private knowledge" not in created.path.read_bytes()

    restored = manager.restore_backup(created.path, tmp_path / "restored-data", PASSPHRASE)
    assert (restored / "knowledge.txt").read_text(encoding="utf-8") == "private knowledge"
    assert (local / "knowledge.txt").read_text(encoding="utf-8") == "private knowledge"


def test_backup_refuses_a_nonremovable_destination(tmp_path) -> None:
    local = tmp_path / "local-data"
    usb = tmp_path / "ordinary-folder"
    local.mkdir()
    usb.mkdir()
    manager = StorageManager(StorageLayout(local, None))
    _expect_error(BackupError, lambda: manager.create_backup(PASSPHRASE, destination_root=usb))
    assert list(usb.iterdir()) == []


def test_wrong_passphrase_and_tampering_never_create_restore_directory(tmp_path) -> None:
    local = tmp_path / "local-data"
    usb = tmp_path / "usb"
    local.mkdir()
    usb.mkdir()
    (local / "note.txt").write_text("secret", encoding="utf-8")
    manager = _manager(local, usb)
    backup = manager.create_backup(PASSPHRASE).path

    destination = tmp_path / "wrong-passphrase-restore"
    _expect_error(ValueError, lambda: manager.restore_backup(backup, destination, "another secure passphrase"))
    assert not destination.exists()

    contents = bytearray(backup.read_bytes())
    contents[-1] ^= 1
    backup.write_bytes(contents)
    _expect_error(ValueError, lambda: manager.restore_backup(backup, destination, PASSPHRASE))
    assert not destination.exists()


def test_restore_rejects_path_traversal_before_writing(tmp_path) -> None:
    local = tmp_path / "local-data"
    usb = tmp_path / "usb"
    local.mkdir()
    usb.mkdir()
    manager = _manager(local, usb)
    content = b"escape"
    document = {
        "format": "robin-encrypted-backup-v1",
        "created_at": "test",
        "files": [{
            "path": "../escaped.txt",
            "size": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "content": base64.b64encode(content).decode("ascii"),
        }],
    }
    backup = usb / "malicious.rbk"
    backup.write_bytes(encrypt_bytes(json.dumps(document).encode("utf-8"), PASSPHRASE))
    destination = tmp_path / "restored-data"

    _expect_error(BackupError, lambda: manager.restore_backup(backup, destination, PASSPHRASE))
    assert not destination.exists()
    assert not (tmp_path / "escaped.txt").exists()
