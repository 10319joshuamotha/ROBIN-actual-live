from robin.core.action import ActionGateway
from robin.core.execution import ExecutionEngine


class FakeAdapter:
    def execute(self, plan):
        return f"executed:{plan.request.action}:{plan.request.resource}"


def test_execution_requires_safe_plan() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    safe = gateway.plan("open_application", "calculator", user_command_id="test-command")
    result = engine.execute(safe, FakeAdapter())
    assert result.executed
    assert "calculator" in result.message


def test_execution_blocks_unapproved_plan() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    sensitive = gateway.plan("delete_file", "important.txt", user_command_id="test-command")
    result = engine.execute(sensitive, FakeAdapter())
    assert not result.executed
    assert "not approved" in result.message
