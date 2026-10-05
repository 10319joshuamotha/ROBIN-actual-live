from __future__ import annotations

from dataclasses import dataclass

from ..security import ActionRequest, PolicyDecision, PolicyEngine, RiskLevel


@dataclass(frozen=True)
class ActionPlan:
    request: ActionRequest
    decision: PolicyDecision


class ActionGateway:
    """Single gateway between ROBIN reasoning and device-side execution."""

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self.policy = policy or PolicyEngine()

    def plan(self, action: str, resource: str = "", reason: str = "") -> ActionPlan:
        request = ActionRequest(action=action, resource=resource, reason=reason)
        return ActionPlan(request, self.policy.evaluate(request))

    def approve(self, plan: ActionPlan) -> ActionPlan:
        decision = self.policy.approve(plan.request)
        return ActionPlan(plan.request, decision)

    @staticmethod
    def can_execute(plan: ActionPlan) -> bool:
        return plan.decision.risk is RiskLevel.SAFE and bool(plan.decision.approval_token or plan.request.action)
