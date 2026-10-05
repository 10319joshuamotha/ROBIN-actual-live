from __future__ import annotations

from dataclasses import dataclass

from ..security import ActionRequest, PolicyDecision, PolicyEngine, RiskLevel


@dataclass(frozen=True)
class ActionPlan:
    request: ActionRequest
    decision: PolicyDecision


class ActionGateway:
    """Single command-bound gateway between ROBIN reasoning and device execution."""

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self.policy = policy or PolicyEngine()

    def plan(
        self,
        action: str,
        resource: str = "",
        reason: str = "",
        *,
        user_command_id: str | None = None,
    ) -> ActionPlan:
        request = ActionRequest(
            action=action,
            resource=resource,
            reason=reason,
            user_command_id=user_command_id,
        )
        return ActionPlan(request, self.policy.evaluate(request))

    def approve(self, plan: ActionPlan, *, user_confirmed: bool = False) -> ActionPlan:
        decision = self.policy.approve(plan.request, user_confirmed=user_confirmed)
        return ActionPlan(plan.request, decision)

    @staticmethod
    def can_execute(plan: ActionPlan) -> bool:
        if plan.decision.risk is not RiskLevel.SAFE or not plan.request.user_command_id:
            return False
        if PolicyEngine.requires_confirmation(plan.request.action):
            return bool(plan.decision.approval_token)
        return True
