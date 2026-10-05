from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .action import ActionGateway, ActionPlan


class ActionAdapter(Protocol):
    """Device adapter contract. Adapters must execute only approved plans."""

    def execute(self, plan: ActionPlan) -> str: ...


@dataclass(frozen=True)
class ExecutionResult:
    executed: bool
    message: str


class ExecutionEngine:
    """Final execution boundary between approved plans and device adapters."""

    def __init__(self, gateway: ActionGateway | None = None) -> None:
        self.gateway = gateway or ActionGateway()

    def execute(self, plan: ActionPlan, adapter: ActionAdapter) -> ExecutionResult:
        if not self.gateway.can_execute(plan):
            return ExecutionResult(False, "Action was not approved for execution.")
        return ExecutionResult(True, adapter.execute(plan))
