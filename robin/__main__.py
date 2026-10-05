from __future__ import annotations

from .config import RobinConfig
from .lifecycle import Lifecycle
from .logging import configure_logging


def main() -> None:
    config = RobinConfig()
    config.ensure_directories()
    logger = configure_logging(config.paths.logs)

    lifecycle = Lifecycle()
    lifecycle.start()
    logger.info("ROBIN foundation online; state=%s", lifecycle.state.value)
    print(f"ROBIN {config.version} | state={lifecycle.state.value}")


if __name__ == "__main__":
    main()
