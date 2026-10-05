from __future__ import annotations

import argparse
from secrets import token_urlsafe

from .config import RobinConfig
from .core.health import check
from .runtime import RobinRuntime


def main() -> None:
    parser = argparse.ArgumentParser(description="ROBIN local assistant runtime")
    parser.add_argument("--command", help="Submit one explicit local command, e.g. 'open calculator'")
    args = parser.parse_args()

    config = RobinConfig()
    health = check(config)
    if not health.ok:
        raise SystemExit("ROBIN foundation health check failed")

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
