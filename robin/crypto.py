from __future__ import annotations

import hashlib
import os
from pathlib import Path
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ENVELOPE_MAGIC = b"ROBINENC1"
_SALT_BYTES = 16
_NONCE_BYTES = 12
_KEY_BYTES = 32
_MIN_PASSPHRASE_BYTES = 12
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


class EncryptedDataError(ValueError):
    """Raised when encrypted ROBIN data is unsupported, damaged, or locked."""


def validate_passphrase(passphrase: str) -> bytes:
    if not isinstance(passphrase, str):
        raise ValueError("Passphrase must be text.")
    encoded = passphrase.encode("utf-8")
    if len(encoded) < _MIN_PASSPHRASE_BYTES:
        raise ValueError("Use a passphrase with at least 12 UTF-8 bytes.")
    if len(encoded) > 4096:
        raise ValueError("Passphrase is too long.")
    return encoded


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    encoded = validate_passphrase(passphrase)
    return hashlib.scrypt(
        encoded,
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        maxmem=64 * 1024 * 1024,
        dklen=_KEY_BYTES,
    )


def encrypt_bytes(plaintext: bytes, passphrase: str) -> bytes:
    if not isinstance(plaintext, bytes):
        raise TypeError("Encrypted content must be bytes.")
    validate_passphrase(passphrase)
    salt = os.urandom(_SALT_BYTES)
    nonce = os.urandom(_NONCE_BYTES)
    key = _derive_key(passphrase, salt)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, ENVELOPE_MAGIC)
    return ENVELOPE_MAGIC + salt + nonce + ciphertext


def decrypt_bytes(envelope: bytes, passphrase: str) -> bytes:
    validate_passphrase(passphrase)
    header_bytes = len(ENVELOPE_MAGIC) + _SALT_BYTES + _NONCE_BYTES
    if len(envelope) < header_bytes + 16 or not envelope.startswith(ENVELOPE_MAGIC):
        raise EncryptedDataError("File is not a supported encrypted ROBIN file.")
    offset = len(ENVELOPE_MAGIC)
    salt = envelope[offset : offset + _SALT_BYTES]
    offset += _SALT_BYTES
    nonce = envelope[offset : offset + _NONCE_BYTES]
    ciphertext = envelope[header_bytes:]
    try:
        return AESGCM(_derive_key(passphrase, salt)).decrypt(nonce, ciphertext, ENVELOPE_MAGIC)
    except InvalidTag:
        raise EncryptedDataError("Passphrase is incorrect or encrypted data is damaged.") from None


def write_atomic(path: Path, data: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
