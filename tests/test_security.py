from robin.security import ActionRequest, PolicyEngine, RiskLevel


def test_payment_credentials_are_denied() -> None:
    decision = PolicyEngine().evaluate(ActionRequest("read_payment_credentials", user_command_id="test-command"))
    assert decision.risk is RiskLevel.DENY


def test_sensitive_action_requires_explicit_confirmation() -> None:
    engine = PolicyEngine()
    request = ActionRequest("delete_file", resource="example.txt", user_command_id="test-command")
    decision = engine.evaluate(request)
    assert decision.risk is RiskLevel.CONFIRM

    pending = engine.approve(request)
    assert pending.risk is RiskLevel.CONFIRM
    assert pending.approval_token is None

    approved = engine.approve(request, user_confirmed=True)
    assert approved.risk is RiskLevel.SAFE
    assert approved.approval_token


def test_normal_action_is_safe_only_with_a_user_command() -> None:
    engine = PolicyEngine()
    assert engine.evaluate(ActionRequest("open_application", resource="calculator")).risk is RiskLevel.DENY
    decision = engine.evaluate(ActionRequest("open_application", resource="calculator", user_command_id="test-command"))
    assert decision.risk is RiskLevel.SAFE
