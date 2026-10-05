from robin.memory import MemoryStore


def test_memory_round_trip(tmp_path) -> None:
    store = MemoryStore(tmp_path / "memory.json")
    store.remember("project", "ROBIN")
    results = store.search("robin")
    assert len(results) == 1
    assert results[0].key == "project"
    assert results[0].value == "ROBIN"
