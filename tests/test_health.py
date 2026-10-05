from robin.config import RobinConfig, RobinPaths
from robin.health import check_health


def test_foundation_health_is_ok(tmp_path) -> None:
    paths = RobinPaths(
        root=tmp_path / "robin",
        data=tmp_path / "robin" / "data",
        logs=tmp_path / "robin" / "logs",
        usb=tmp_path / "robin" / "usb",
    )
    config = RobinConfig(paths=paths)
    config.ensure_directories()
    report = check_health(config)
    assert report.ok
    assert report.storage_model == "local-runtime-plus-portable-master-backup"
