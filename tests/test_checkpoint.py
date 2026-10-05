from robin.core.checkpoint import CheckpointStore


def test_checkpoint_is_created(tmp_path) -> None:
    checkpoint = CheckpointStore(tmp_path).create("before upgrade")
    assert checkpoint.identifier.startswith("checkpoint-")
    assert checkpoint.path.is_dir()
    assert (checkpoint.path / "description.txt").read_text(encoding="utf-8") == "before upgrade"
