from robin.core.brain import Brain
from robin.core.intent import IntentType


def test_brain_handles_deterministic_intents() -> None:
    decision = Brain().decide("go to sleep")
    assert decision.intent.kind is IntentType.SLEEP
    assert "sleep" in decision.response.casefold()


def test_brain_does_not_claim_model_capability_yet() -> None:
    decision = Brain().decide("hello robin")
    assert decision.intent.kind is IntentType.CONVERSATION
    assert "not configured" in decision.response
