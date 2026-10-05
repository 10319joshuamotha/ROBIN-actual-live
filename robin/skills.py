from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    TESTING = "testing"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class UpgradeProposal:
    name: str
    summary: str
    status: ProposalStatus = ProposalStatus.DRAFT


class SkillRegistry:
    """Registry boundary for learned capabilities; execution adapters come later."""

    def __init__(self) -> None:
        self._skills: dict[str, str] = {}

    def register(self, name: str, description: str) -> None:
        self._skills[name] = description

    def list(self) -> dict[str, str]:
        return dict(self._skills)

    def propose_upgrade(self, name: str, summary: str) -> UpgradeProposal:
        return UpgradeProposal(name=name, summary=summary)
