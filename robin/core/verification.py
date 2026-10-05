from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .action import ActionPlan


class VerificationStatus(str, Enum):
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    message: str


class ActionVerifier:
    """Contract for post-action verification.

    Device adapters will supply observed state later. The verifier is kept
    separate from execution so an action is not considered successful merely
    because a command was sent to the operating system.
    """

    def verify(self, plan: ActionPlan, observed: object | None = None) -> VerificationResult:
        if observed is None:
            return VerificationResult(
                VerificationStatus.NOT_RUN,
                f"Action '{plan.request.action}' has not been verified.",
            )
        return VerificationResult(VerificationStatus.PASSED, "Observed result accepted.")
