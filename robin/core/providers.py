from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ReasoningProvider(Protocol):
    """Provider contract for a future local or remote language model."""

    def respond(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class ProviderStatus:
    name: str
    available: bool
    local: bool


class NullProvider:
    """Safe placeholder until a real model provider is deliberately configured."""

    status = ProviderStatus(name="none", available=False, local=True)

    def respond(self, prompt: str) -> str:
        raise RuntimeError("No reasoning provider is configured.")
