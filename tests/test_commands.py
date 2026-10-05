from robin.commands import CommandParser


def test_open_command_is_parsed_deterministically() -> None:
    command = CommandParser().parse("Open Calculator")
    assert command.name == "open_application"
    assert command.argument == "calculator"


def test_unrecognized_text_is_not_converted_to_an_action() -> None:
    command = CommandParser().parse("delete my files")
    assert command.name == "conversation"
