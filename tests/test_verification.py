from robin.core.action import ActionGateway
from robin.core.verification import ActionVerifier, VerificationStatus


def test_action_is_not_successful_without_observation() -> None:
    gateway = ActionGateway()
    plan = gateway.plan("open_application", "calculator")
    result = ActionVerifier().verify(plan)
    assert result.status is VerificationStatus.NOT_RUN


def test_action_can_be_verified_after_observation() -> None:
    gateway = ActionGateway()
    plan = gateway.plan("open_application", "calculator")
    result = ActionVerifier().verify(plan, observed={"application": "calculator", "visible": True})
    assert result.status is VerificationStatus.PASSED
