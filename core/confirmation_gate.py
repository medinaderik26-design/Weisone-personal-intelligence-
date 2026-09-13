"""PI-045 explicit human confirmation gates for consequential actions."""

from dataclasses import dataclass
from typing import Optional

from .side_effect_registry import SideEffectProfile


@dataclass(frozen=True)
class ConfirmationRequest:
    task_id: str
    operation: str
    reason: str
    requires_confirmation: bool


@dataclass(frozen=True)
class ConfirmationDecision:
    task_id: str
    allowed: bool
    reason: str


class ConfirmationGate:
    """Require explicit human approval for consequential operations."""

    def request(self, task_id: str, profile: SideEffectProfile, *, reason: Optional[str] = None) -> ConfirmationRequest:
        if not task_id:
            raise ValueError("task_id is required")
        return ConfirmationRequest(
            task_id=task_id,
            operation=profile.operation,
            reason=reason or profile.description or "operation requires confirmation",
            requires_confirmation=profile.requires_confirmation,
        )

    def decide(self, request: ConfirmationRequest, *, confirmed: bool) -> ConfirmationDecision:
        if request.requires_confirmation and not confirmed:
            return ConfirmationDecision(request.task_id, False, "explicit confirmation required")
        if request.requires_confirmation and confirmed:
            return ConfirmationDecision(request.task_id, True, "explicit confirmation received")
        return ConfirmationDecision(request.task_id, True, "operation does not require confirmation")
