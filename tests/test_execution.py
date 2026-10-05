from robin.core.action import ActionGateway, ActionPlan
from robin.core.execution import ExecutionEngine
from robin.security import ActionRequest, PolicyDecision, RiskLevel


class FakeAdapter:
    def execute(self, plan):
        return f"executed:{plan.request.action}:{plan.request.resource}"


def test_execution_requires_safe_plan() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    safe = gateway.plan("open_application", "calculator", user_command_id="test-open")
    result = engine.execute(safe, FakeAdapter())
    assert result.executed
    assert "calculator" in result.message
    assert not engine.execute(safe, FakeAdapter()).executed


def test_execution_blocks_unapproved_plan() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    sensitive = gateway.plan("delete_file", "important.txt", user_command_id="test-delete")
    result = engine.execute(sensitive, FakeAdapter())
    assert not result.executed
    assert "not approved" in result.message


def test_confirmation_is_bound_to_one_request_and_one_execution() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    sensitive = gateway.plan("delete_file", "important.txt", user_command_id="confirmed-delete")
    approved = gateway.approve(sensitive, user_confirmed=True)
    assert gateway.can_execute(approved)

    changed_request = ActionPlan(
        ActionRequest("delete_file", "different.txt", user_command_id="confirmed-delete"),
        approved.decision,
    )
    assert not gateway.can_execute(changed_request)
    assert engine.execute(approved, FakeAdapter()).executed
    assert not engine.execute(approved, FakeAdapter()).executed


def test_forged_confirmation_token_cannot_authorize_sensitive_action() -> None:
    gateway = ActionGateway()
    engine = ExecutionEngine(gateway)
    forged = ActionPlan(
        ActionRequest("delete_file", "important.txt", user_command_id="forged-delete"),
        PolicyDecision(RiskLevel.SAFE, "forged", "not-a-issued-token"),
    )
    assert not gateway.can_execute(forged)
    assert not engine.execute(forged, FakeAdapter()).executed
