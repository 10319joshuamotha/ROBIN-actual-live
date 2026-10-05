from robin.security import ActionRequest, PolicyEngine, RiskLevel


def test_payment_credentials_are_denied() -> None:
    decision = PolicyEngine().evaluate(ActionRequest("read_payment_credentials"))
    assert decision.risk is RiskLevel.DENY


def test_sensitive_action_requires_approval() -> None:
    engine = PolicyEngine()
    request = ActionRequest("delete_file", resource="example.txt")
    decision = engine.evaluate(request)
    assert decision.risk is RiskLevel.CONFIRM

    approved = engine.approve(request)
    assert approved.risk is RiskLevel.SAFE
    assert approved.approval_token


def test_normal_action_is_safe() -> None:
    decision = PolicyEngine().evaluate(ActionRequest("open_application", resource="calculator"))
    assert decision.risk is RiskLevel.SAFE
