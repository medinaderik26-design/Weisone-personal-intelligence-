"""PI-026 scheduler-facing recovery controller.

Consumes recovery decisions and produces explicit scheduler actions. It never
executes a task itself; execution remains behind the normal permission and
idempotency boundaries.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .recovery_coordinator import RecoveryAction, RecoveryDecision


class SchedulerAction(str, Enum):
    ENQUEUE = "enqueue"
    RETRY = "retry"
    REROUTE = "reroute"
    DEFER = "defer"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class ScheduledRecovery:
    task_id: str
    action: SchedulerAction
    provider: Optional[str]
    reason: str


class SchedulerRecoveryController:
    """Translate recovery decisions into safe queue operations."""

    def apply(self, decision: RecoveryDecision) -> ScheduledRecovery:
        mapping = {
            RecoveryAction.RESUME: SchedulerAction.ENQUEUE,
            RecoveryAction.RETRY: SchedulerAction.RETRY,
            RecoveryAction.REROUTE: SchedulerAction.REROUTE,
            RecoveryAction.DEFER: SchedulerAction.DEFER,
            RecoveryAction.HUMAN_REVIEW: SchedulerAction.HUMAN_REVIEW,
        }
        return ScheduledRecovery(
            task_id=decision.task_id,
            action=mapping[decision.action],
            provider=decision.provider,
            reason=decision.reason,
        )
