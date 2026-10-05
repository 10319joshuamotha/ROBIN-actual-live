from __future__ import annotations

from dataclasses import dataclass

from .commands import Command, CommandParser
from .config import RobinConfig
from .core.action import ActionGateway
from .core.execution import ActionAdapter, ExecutionEngine
from .core.windows_adapter import WindowsActionAdapter
from .lifecycle import Lifecycle, LifecycleState
from .logging import configure_logging


@dataclass(frozen=True)
class RuntimeResult:
    command: Command
    state: LifecycleState
    message: str


class RobinRuntime:
    """Small host runtime; device actions require an explicit user command."""

    def __init__(
        self,
        config: RobinConfig | None = None,
        action_adapter: ActionAdapter | None = None,
    ) -> None:
        self.config = config or RobinConfig()
        self.config.ensure_directories()
        self.logger = configure_logging(self.config.paths.logs)
        self.lifecycle = Lifecycle()
        self.parser = CommandParser()
        self.gateway = ActionGateway()
        self.execution = ExecutionEngine(self.gateway)
        self.action_adapter = action_adapter or WindowsActionAdapter()

    def start(self) -> RuntimeResult:
        self.lifecycle.start()
        return RuntimeResult(Command("start"), self.lifecycle.state, "ROBIN is online.")

    def handle(self, text: str, *, user_command_id: str | None = None) -> RuntimeResult:
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

        if command.name == "open_application":
            plan = self.gateway.plan(
                command.name,
                command.argument,
                reason="User typed an explicit open command.",
                user_command_id=user_command_id,
            )
            if not self.gateway.can_execute(plan):
                return RuntimeResult(command, self.lifecycle.state, f"Action blocked. {plan.decision.explanation}")
            try:
                result = self.execution.execute(plan, self.action_adapter)
            except (OSError, RuntimeError, ValueError) as error:
                return RuntimeResult(command, self.lifecycle.state, f"Action not performed. {error}")
            return RuntimeResult(command, self.lifecycle.state, result.message)

        return RuntimeResult(command, self.lifecycle.state, "I can't perform that task yet. Nothing was sent or changed.")

    def wake_with_key(self, key: str = "ESC") -> RuntimeResult:
        command = Command("wake", key)
        if self.lifecycle.wake(key):
            return RuntimeResult(command, self.lifecycle.state, "ROBIN is awake and listening.")
        return RuntimeResult(command, self.lifecycle.state, "Wake request ignored.")
