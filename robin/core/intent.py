from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IntentType(str, Enum):
    CONVERSATION = "conversation"
    SLEEP = "sleep"
    WAKE = "wake"
    STATUS = "status"
    HEALTH = "health"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Intent:
    kind: IntentType
    text: str
    confidence: float = 1.0


class IntentParser:
    """Minimal deterministic intent layer; model-backed understanding comes later."""

    def parse(self, text: str) -> Intent:
        normalized = " ".join(text.strip().casefold().split())
        mapping = {
            "sleep": IntentType.SLEEP,
            "go to sleep": IntentType.SLEEP,
            "wake up": IntentType.WAKE,
            "status": IntentType.STATUS,
            "health": IntentType.HEALTH,
        }
        if normalized in mapping:
            return Intent(mapping[normalized], text.strip())
        if normalized:
            return Intent(IntentType.CONVERSATION, text.strip(), 0.5)
        return Intent(IntentType.UNKNOWN, text, 0.0)
