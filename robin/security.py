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
    user_command_id: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    risk: RiskLevel
    explanation: str
    approval_token: str | None = None


class PolicyEngine:
    """Command-bound safety gate; unknown actions fail closed."""

    ALWAYS_DENY = {
        "read_payment_credentials",
        "export_credentials",
        "bypass_payment_auth",
        "make_payment",
        "submit_payment",
        "transfer_funds",
        "use_gpay",
        "scan_gallery",
        "enumerate_gallery",
        "read_entire_gallery",
    }
    FINANCIAL_TOKENS = {"payment", "payments", "gpay", "purchase", "purchases", "transaction", "transactions"}
    CREDENTIAL_TOKENS = {"credential", "credentials", "secret", "secrets", "password", "passwords", "token", "tokens"}
    GALLERY_BULK_TOKENS = {"scan", "enumerate", "index", "export", "all", "bulk"}
    CONFIRM_PREFIXES = {
        "delete_",
        "send_",
        "modify_security_",
        "install_code_",
        "activate_upgrade",
        "pair_device",
        "grant_gallery_access",
        "open_selected_photo",
        "read_selected_photo",
        "view_selected_photo",
        "capture_screen",
        "export_file",
        "upload_file",
        "close_application",
    }
    SAFE_APPLICATIONS = {"calculator", "notepad", "file explorer"}
    SAFE_ACTIONS = {"open_application", "status", "health"}

    @staticmethod
    def _normalize(action: str) -> str:
        return "_".join(action.strip().casefold().replace("-", "_").split())

    @classmethod
    def requires_confirmation(cls, action: str) -> bool:
        normalized = cls._normalize(action)
        return any(normalized.startswith(prefix) for prefix in cls.CONFIRM_PREFIXES)

    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        action = self._normalize(request.action)
        if not request.user_command_id or not request.user_command_id.strip():
            return PolicyDecision(RiskLevel.DENY, "An explicit user command is required; autonomous actions are blocked.")

        tokens = set(action.split("_"))
        if action in self.ALWAYS_DENY or tokens & self.FINANCIAL_TOKENS or tokens & self.CREDENTIAL_TOKENS:
            return PolicyDecision(RiskLevel.DENY, "Financial actions and credential access are outside ROBIN's trust boundary.")
        if "gallery" in tokens and tokens & self.GALLERY_BULK_TOKENS:
            return PolicyDecision(RiskLevel.DENY, "Bulk gallery access is blocked; only a specifically selected item may be requested.")
        if self.requires_confirmation(action):
            return PolicyDecision(RiskLevel.CONFIRM, "Explicit user approval is required for this sensitive action.")
        if action == "open_application":
            app = " ".join(request.resource.strip().casefold().split())
            if app not in self.SAFE_APPLICATIONS:
                return PolicyDecision(RiskLevel.DENY, "That application is not explicitly allowlisted.")
        if action in self.SAFE_ACTIONS:
            return PolicyDecision(RiskLevel.SAFE, "Action is explicitly allowlisted and bound to a user command.")
        return PolicyDecision(RiskLevel.DENY, "Action is not explicitly allowlisted.")

    def approve(self, request: ActionRequest, *, user_confirmed: bool = False) -> PolicyDecision:
        decision = self.evaluate(request)
        if decision.risk is not RiskLevel.CONFIRM or not user_confirmed:
            return decision
        token = f"{token_urlsafe(24)}:{int(time())}"
        return PolicyDecision(RiskLevel.SAFE, "User confirmation recorded for this request.", token)
