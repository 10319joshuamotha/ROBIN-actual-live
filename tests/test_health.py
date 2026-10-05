from robin.config import RobinConfig, RobinPaths
from robin.health import check_health


def test_local_health_stays_ok_when_usb_is_absent(tmp_path) -> None:
    paths = RobinPaths(
        root=tmp_path / "robin",
        data=tmp_path / "robin" / "data",
        logs=tmp_path / "robin" / "logs",
        usb=None,
    )
    config = RobinConfig(paths=paths)
    config.ensure_directories()
    report = check_health(config)
    assert report.ok
    assert not report.usb_path
    assert report.storage_model == "local-first-with-encrypted-removable-backup"
