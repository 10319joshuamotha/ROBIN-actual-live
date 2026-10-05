from robin.crypto import EncryptedDataError, ENVELOPE_MAGIC
from robin.memory import MemoryStore


PASSPHRASE = "correct horse battery staple"


def test_memory_round_trip(tmp_path) -> None:
    path = tmp_path / "memory.enc"
    store = MemoryStore(path, PASSPHRASE)
    store.remember("project", "ROBIN")
    results = store.search("robin")
    assert len(results) == 1
    assert results[0].key == "project"
    assert results[0].value == "ROBIN"
    assert path.read_bytes().startswith(ENVELOPE_MAGIC)
    assert b"ROBIN" not in path.read_bytes()


def test_wrong_passphrase_does_not_overwrite_local_memory(tmp_path) -> None:
    path = tmp_path / "memory.enc"
    MemoryStore(path, PASSPHRASE).remember("project", "private note")
    before = path.read_bytes()
    try:
        MemoryStore(path, "different secure passphrase").remember("other", "value")
    except EncryptedDataError:
        pass
    else:
        raise AssertionError("Wrong passphrase should not load or overwrite memory")
    assert path.read_bytes() == before


def test_legacy_plaintext_memory_is_not_silently_rewritten(tmp_path) -> None:
    path = tmp_path / "memory.json"
    path.write_text('[{"key":"old","value":"plain text","created_at":"now"}]', encoding="utf-8")
    before = path.read_bytes()
    try:
        MemoryStore(path, PASSPHRASE).remember("new", "value")
    except EncryptedDataError:
        pass
    else:
        raise AssertionError("Unencrypted legacy data must be preserved for explicit migration")
    assert path.read_bytes() == before
