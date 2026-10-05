from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path
from secrets import token_urlsafe

from .config import RobinConfig
from .core.health import check
from .crypto import validate_passphrase
from .runtime import RobinRuntime
from .storage import StorageLayout, StorageManager


def _prompt_passphrase(*, confirm: bool) -> str:
    first = getpass("Backup passphrase: ")
    try:
        validate_passphrase(first)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    if confirm:
        second = getpass("Confirm backup passphrase: ")
        if first != second:
            raise SystemExit("Passphrases do not match; no backup was created.")
    return first


def main() -> None:
    parser = argparse.ArgumentParser(description="ROBIN local assistant runtime")
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument("--command", help="Submit one explicit local command, e.g. open calculator")
    operation.add_argument("--backup-to", type=Path, help="Create an encrypted backup on a removable Windows drive")
    operation.add_argument("--restore-from", type=Path, help="Restore an encrypted backup into a new directory")
    parser.add_argument("--restore-to", type=Path, help="New directory for restore; it must not already exist")
    args = parser.parse_args()

    if args.restore_to and not args.restore_from:
        parser.error("--restore-to can only be used with --restore-from")
    if args.restore_from and not args.restore_to:
        parser.error("--restore-from requires --restore-to")

    config = RobinConfig()
    health = check(config)
    if not health.ok:
        raise SystemExit("ROBIN local foundation health check failed")

    storage = StorageManager(StorageLayout(config.paths.data, config.paths.usb))
    if args.backup_to:
        passphrase = _prompt_passphrase(confirm=True)
        try:
            result = storage.create_backup(passphrase, destination_root=args.backup_to)
        except (OSError, ValueError) as error:
            raise SystemExit(f"Backup not created: {error}") from None
        print(f"Encrypted backup created: {result.path} ({result.file_count} files).")
        return

    if args.restore_from:
        passphrase = _prompt_passphrase(confirm=False)
        try:
            destination = storage.restore_backup(args.restore_from, args.restore_to, passphrase)
        except (OSError, ValueError) as error:
            raise SystemExit(f"Restore not completed: {error}") from None
        print(f"Backup restored into new directory: {destination}. Existing local data was not changed.")
        return

    runtime = RobinRuntime(config)
    result = runtime.start()
    print(result.message)
    print(f"State: {result.state.value}")
    if args.command:
        command_result = runtime.handle(
            args.command,
            user_command_id=token_urlsafe(16),
        )
        print(command_result.message)


if __name__ == "__main__":
    main()
