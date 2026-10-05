from __future__ import annotations

from enum import Enum


class LifecycleState(str, Enum):
    STARTING = "starting"
    DORMANT = "dormant"
    LISTENING = "listening"
    THINKING = "thinking"
    ACTING = "acting"
    SLEEPING = "sleeping"
    STOPPED = "stopped"


class Lifecycle:
    """Small deterministic state machine for the assistant runtime."""

    def __init__(self) -> None:
        self.state = LifecycleState.STARTING

    def start(self) -> None:
        if self.state in {LifecycleState.STARTING, LifecycleState.STOPPED}:
            self.state = LifecycleState.DORMANT

    def sleep(self) -> None:
        self.state = LifecycleState.SLEEPING

    def wake(self, key: str) -> bool:
        if self.state is LifecycleState.SLEEPING and key.upper() == "ESC":
            self.state = LifecycleState.LISTENING
            return True
        return False

    def begin_listening(self) -> None:
        if self.state is not LifecycleState.SLEEPING:
            self.state = LifecycleState.LISTENING

    def begin_thinking(self) -> None:
        if self.state is not LifecycleState.SLEEPING:
            self.state = LifecycleState.THINKING

    def begin_action(self) -> None:
        if self.state is not LifecycleState.SLEEPING:
            self.state = LifecycleState.ACTING

    def return_dormant(self) -> None:
        if self.state is not LifecycleState.SLEEPING:
            self.state = LifecycleState.DORMANT

    def stop(self) -> None:
        self.state = LifecycleState.STOPPED
