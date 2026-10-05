from __future__ import annotations

from dataclasses import dataclass

from .commands import Command, CommandParser
from .config import RobinConfig
from .lifecycle import Lifecycle, LifecycleState
from .logging import configure_logging


@dataclass(frozen=True)
class RuntimeResult:
    command: Command
    state: LifecycleState
    message: str


class RobinRuntime:
    """Small host runtime that wires lifecycle and deterministic commands together."""

    def __init__(self, config: RobinConfig | None = None) -> None:
        self.config = config or RobinConfig()
        self.config.ensure_directories()
        self.logger = configure_logging(self.config.paths.logs)
        self.lifecycle = Lifecycle()
        self.parser = CommandParser()

    def start(self) -> RuntimeResult:
        self.lifecycle.start()
        return RuntimeResult(Command("start"), self.lifecycle.state, "ROBIN is online.")

    def handle(self, text: str) -> RuntimeResult:
        command = self.parser.parse(text)

        if self.lifecycle.state is LifecycleState.SLEEPING:
            return RuntimeResult(command, self.lifecycle.state, "ROBIN is sleeping. Press ESC to wake her.")

        if command.name == "sleep":
            self.lifecycle.sleep()
            return RuntimeResult(command, self.lifecycle.state, "ROBIN is going to sleep.")

        if command.name == "wake":
            return RuntimeResult(command, self.lifecycle.state, "ROBIN is already awake.")

        if command.name == "status":
            return RuntimeResult(command, self.lifecycle.state, f"ROBIN state: {self.lifecycle.state.value}.")

        if command.name == "health":
            return RuntimeResult(command, self.lifecycle.state, "ROBIN foundation health: OK.")

        return RuntimeResult(command, self.lifecycle.state, "Command accepted by the runtime boundary.")

    def wake_with_key(self, key: str = "ESC") -> RuntimeResult:
        command = Command("wake", key)
        if self.lifecycle.wake(key):
            return RuntimeResult(command, self.lifecycle.state, "ROBIN is awake and listening.")
        return RuntimeResult(command, self.lifecycle.state, "Wake request ignored.")
