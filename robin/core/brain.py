from __future__ import annotations

from dataclasses import dataclass

from .intent import Intent, IntentParser, IntentType


@dataclass(frozen=True)
class BrainDecision:
    intent: Intent
    response: str


class Brain:
    """Provider-neutral reasoning shell.

    A model provider can be attached later without bypassing the runtime or
    security gateway. This layer currently handles only deterministic intents.
    """

    def __init__(self, intent_parser: IntentParser | None = None) -> None:
        self.intent_parser = intent_parser or IntentParser()

    def decide(self, text: str) -> BrainDecision:
        intent = self.intent_parser.parse(text)
        responses = {
            IntentType.SLEEP: "ROBIN is going to sleep.",
            IntentType.WAKE: "ROBIN is ready.",
            IntentType.STATUS: "ROBIN status requested.",
            IntentType.HEALTH: "ROBIN health requested.",
            IntentType.CONVERSATION: "Conversation received; no model provider is configured yet.",
            IntentType.UNKNOWN: "I need a clearer instruction.",
        }
        return BrainDecision(intent, responses[intent.kind])
