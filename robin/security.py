from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from secrets import token_urlsafe
from time import time


class RiskLevel(str, Enum):
    SAFE = "safe"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass(frozen=True)
class ActionRequest:
    action: str
    resource: str = ""
    reason: str = ""


@dataclass(frozen=True)
class PolicyDecision:
    risk: RiskLevel
    explanation: str
    approval_token: str | None = None


class PolicyEngine:
    """Initial safety boundary; real device adapters will be added later."""

    ALWAYS_DENY = {"read_payment_credentials", "export_credentials", "bypass_payment_auth"}
    CONFIRM_PREFIXES = {
        "delete_",
        "send_",
        "modify_security_",
        "install_code_",
        "activate_upgrade",
        "pair_device",
        "grant_gallery_access",
    }

    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        if request.action in self.ALWAYS_DENY:
            return PolicyDecision(RiskLevel.DENY, "Action is outside ROBIN's trust boundary.")
        if any(request.action.startswith(prefix) for prefix in self.CONFIRM_PREFIXES):
            return PolicyDecision(RiskLevel.CONFIRM, "Explicit user approval is required.")
        return PolicyDecision(RiskLevel.SAFE, "Action is within the initial safe-action boundary.")

    def approve(self, request: ActionRequest) -> PolicyDecision:
        decision = self.evaluate(request)
        if decision.risk is not RiskLevel.CONFIRM:
            return decision
        token = f"{token_urlsafe(24)}:{int(time())}"
        return PolicyDecision(RiskLevel.SAFE, "User approval recorded for this request.", token)
