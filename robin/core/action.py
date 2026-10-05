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

    def can_execute(self, plan: ActionPlan) -> bool:
        if plan.decision.risk is not RiskLevel.SAFE:
            return False
        return self.policy.can_execute(plan.request, plan.decision.approval_token)

    def claim_for_execution(self, plan: ActionPlan) -> bool:
        if plan.decision.risk is not RiskLevel.SAFE:
            return False
        return self.policy.claim_execution(plan.request, plan.decision.approval_token)
