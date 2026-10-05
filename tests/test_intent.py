from robin.core.intent import IntentParser, IntentType


def test_known_commands_have_deterministic_intents() -> None:
    parser = IntentParser()
    assert parser.parse("go to sleep").kind is IntentType.SLEEP
    assert parser.parse("status").kind is IntentType.STATUS
    assert parser.parse("health").kind is IntentType.HEALTH


def test_normal_text_remains_conversation() -> None:
    intent = IntentParser().parse("hello robin")
    assert intent.kind is IntentType.CONVERSATION
    assert intent.text == "hello robin"
