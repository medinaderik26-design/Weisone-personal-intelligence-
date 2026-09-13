"""PI-022 recovery decisions for unfinished work."""

from dataclasses import dataclass
from typing import Literal, Optional

from .persistent_work_state import WorkState

RecoveryAction = Literal["resume", "retry", "reroute", "defer", "human_review"]


@dataclass(frozen=True)
class RecoveryDecision:
    task_id: str
    action: RecoveryAction
    reason: str
    provider: Optional[str] = None


class RecoveryCoordinator:
    """Translate recovered work state into an explicit next action.

    The coordinator does not execute work. It makes the recovery decision so
    execution remains behind the existing scheduler and idempotency boundary.
    """

    def decide(self, state: WorkState, *, provider_available: bool = True,
               retry_allowed: bool = True, reroute_available: bool = False,
               external_completion_unknown: bool = True) -> RecoveryDecision:
        state.validate()

        if state.status == "completed":
            return RecoveryDecision(state.task_id, "human_review", "completed work should not be recovered")

        if external_completion_unknown and state.status == "running":
            if reroute_available:
                return RecoveryDecision(state.task_id, "reroute", "completion state is unknown and an alternate provider is available")
            return RecoveryDecision(state.task_id, "human_review", "completion state is unknown; external side effect must be verified")

        if state.status == "queued":
            if provider_available:
                return RecoveryDecision(state.task_id, "resume", "queued work can resume")
            return RecoveryDecision(state.task_id, "defer", "no provider is currently available")

        if state.status == "failed":
            if retry_allowed and provider_available:
                return RecoveryDecision(state.task_id, "retry", "failure is retryable and capacity is available")
            if reroute_available:
                return RecoveryDecision(state.task_id, "reroute", "retry is unavailable but an alternate provider exists")
            return RecoveryDecision(state.task_id, "defer", "work cannot safely execute now")

        return RecoveryDecision(state.task_id, "human_review", "no safe automatic recovery action")
