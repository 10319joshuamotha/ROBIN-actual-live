from robin.core.action import ActionGateway
from robin.security import RiskLevel


def test_safe_action_requires_a_user_command_and_can_execute() -> None:
    gateway = ActionGateway()
    plan = gateway.plan("open_application", "calculator", user_command_id="command-1")
    assert plan.decision.risk is RiskLevel.SAFE
    assert gateway.can_execute(plan)


def test_sensitive_action_requires_user_confirmation() -> None:
    gateway = ActionGateway()
    plan = gateway.plan("delete_file", "example.txt", user_command_id="command-2")
    assert plan.decision.risk is RiskLevel.CONFIRM
    assert not gateway.can_execute(plan)

    still_pending = gateway.approve(plan)
    assert still_pending.decision.risk is RiskLevel.CONFIRM
    assert not gateway.can_execute(still_pending)

    approved = gateway.approve(plan, user_confirmed=True)
    assert approved.decision.risk is RiskLevel.SAFE
    assert approved.decision.approval_token
    assert gateway.can_execute(approved)


def test_actions_without_a_user_command_are_denied() -> None:
    plan = ActionGateway().plan("open_application", "calculator")
    assert plan.decision.risk is RiskLevel.DENY
    assert not ActionGateway.can_execute(plan)


def test_unknown_actions_fail_closed() -> None:
    plan = ActionGateway().plan("run_arbitrary_shell", user_command_id="command-3")
    assert plan.decision.risk is RiskLevel.DENY
    assert not ActionGateway.can_execute(plan)


def test_financial_actions_are_hard_denied() -> None:
    gateway = ActionGateway()
    for action in ("read_payment_credentials", "make_payment", "use_gpay", "transfer_funds"):
        plan = gateway.plan(action, user_command_id="command-4")
        assert plan.decision.risk is RiskLevel.DENY
        assert not gateway.can_execute(plan)


def test_bulk_gallery_access_is_denied_and_single_item_requires_confirmation() -> None:
    gateway = ActionGateway()
    bulk = gateway.plan("scan_gallery", user_command_id="command-5")
    assert bulk.decision.risk is RiskLevel.DENY

    selected = gateway.plan("view_selected_photo", "photo-1", user_command_id="command-6")
    assert selected.decision.risk is RiskLevel.CONFIRM
    assert not gateway.can_execute(selected)
