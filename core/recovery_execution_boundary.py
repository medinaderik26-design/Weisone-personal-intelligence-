"""PI-066 execution boundary for drift-aware recovery scheduling."""

from dataclasses import dataclass

from .recovery_coordinator import RecoveryDecision
from .recovery_policy import RecoveryPolicyDecision
from .scheduler_recovery import SchedulerAction, ScheduledRecovery, SchedulerRecoveryController


@dataclass(frozen=True)
class RecoveryBoundaryResult:
    scheduled: ScheduledRecovery
    policy: RecoveryPolicyDecision


class RecoveryExecutionBoundary:
    """Prevent ambiguous recovery drift from reaching automatic execution."""

    def __init__(self, controller: SchedulerRecoveryController | None = None) -> None:
        self.controller = controller or SchedulerRecoveryController()

    def apply(
        self,
        decision: RecoveryDecision,
        policy: RecoveryPolicyDecision,
    ) -> RecoveryBoundaryResult:
        if policy.action == "continue":
            scheduled = self.controller.apply(decision)
        elif policy.action == "reinspect":
            scheduled = ScheduledRecovery(
                task_id=decision.task_id,
                action=SchedulerAction.DEFER,
                provider=decision.provider,
                reason=policy.reason,
            )
        else:
            scheduled = ScheduledRecovery(
                task_id=decision.task_id,
                action=SchedulerAction.HUMAN_REVIEW,
                provider=decision.provider,
                reason=policy.reason,
            )

        return RecoveryBoundaryResult(scheduled=scheduled, policy=policy)
