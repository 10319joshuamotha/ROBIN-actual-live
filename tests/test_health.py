from robin.config import RobinConfig
from robin.health import check_health


def test_foundation_health_is_ok(tmp_path) -> None:
    config = RobinConfig(paths=RobinConfig().paths)
    config.ensure_directories()
    report = check_health(config)
    assert report.ok
    assert report.storage_model == "local-runtime-plus-portable-master-backup"
