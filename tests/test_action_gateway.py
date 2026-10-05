from robin.core.action import ActionGateway
from robin.security import RiskLevel


def test_safe_action_can_be_executed() -> None:
    plan = ActionGateway().plan("open_application", "calculator")
    assert plan.decision.risk is RiskLevel.SAFE
    assert ActionGateway.can_execute(plan)


def test_sensitive_action_requires_approval() -> None:
    gateway = ActionGateway()
    plan = gateway.plan("delete_file", "example.txt")
    assert plan.decision.risk is RiskLevel.CONFIRM
    assert not gateway.can_execute(plan)

    approved = gateway.approve(plan)
    assert approved.decision.risk is RiskLevel.SAFE
    assert approved.decision.approval_token
    assert gateway.can_execute(approved)


def test_payment_credentials_remain_denied() -> None:
    plan = ActionGateway().plan("read_payment_credentials")
    assert plan.decision.risk is RiskLevel.DENY
    assert not ActionGateway.can_execute(plan)
