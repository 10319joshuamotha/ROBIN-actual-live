from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    argument: str = ""


class CommandParser:
    """Deterministic command hints used before a real language/intent layer exists."""

    _prefixes = (
        ("go to sleep", "sleep"),
        ("sleep", "sleep"),
        ("wake up", "wake"),
        ("status", "status"),
        ("health", "health"),
    )

    def parse(self, text: str) -> Command:
        normalized = " ".join(text.strip().casefold().split())
        for prefix, name in self._prefixes:
            if normalized == prefix:
                return Command(name)
            if normalized.startswith(prefix + " "):
                return Command(name, normalized[len(prefix) + 1 :])
        if normalized.startswith("open "):
            return Command("open_application", normalized[5:].strip())
        return Command("conversation", text.strip())
