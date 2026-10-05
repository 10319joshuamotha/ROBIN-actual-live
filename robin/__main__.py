from .config import RobinConfig
from .core.health import check
from .runtime import RobinRuntime


def main() -> None:
    config = RobinConfig()
    health = check(config)
    if not health.ok:
        raise SystemExit("ROBIN foundation health check failed")

    runtime = RobinRuntime(config)
    result = runtime.start()
    print(result.message)
    print(f"State: {result.state.value}")


if __name__ == "__main__":
    main()
