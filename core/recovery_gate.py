"""PI-023 recovery execution gate.

Combines recovery decisions, idempotency, and retry policy without executing
external work itself. This keeps dangerous side effects behind explicit gates.
"""

from dataclasses import dataclass
from typing import Optional

from .idempotency import IdempotencyRegistry
from .persistent_work_state import WorkState
from .recovery_coordinator import RecoveryAction, RecoveryCoordinator, RecoveryDecision
from .retry_policy import RetryPolicy


@dataclass(frozen=True)
class RecoveryGateResult:
    decision: RecoveryDecision
    execution_allowed: bool
    reason: str


class RecoveryExecutionGate:
    def __init__(
        self,
        coordinator: RecoveryCoordinator,
        idempotency: IdempotencyRegistry,
        retry_policy: Optional[RetryPolicy] = None,
    ) -> None:
        self.coordinator = coordinator
        self.idempotency = idempotency
        self.retry_policy = retry_policy or RetryPolicy()

    def evaluate(
        self,
        state: WorkState,
        *,
        execution_key: str,
        provider_available: bool = True,
        reroute_available: bool = False,
        external_completion_unknown: bool = True,
        retryable: bool = True,
    ) -> RecoveryGateResult:
        decision = self.coordinator.decide(
            state,
            provider_available=provider_available,
            retry_allowed=retryable,
            reroute_available=reroute_available,
            external_completion_unknown=external_completion_unknown,
        )

        if self.idempotency.completed(execution_key):
            return RecoveryGateResult(
                decision,
                False,
                "execution key already has a successful receipt",
            )

        if decision.action in {RecoveryAction.HUMAN_REVIEW, "human_review"}:
            return RecoveryGateResult(decision, False, decision.reason)

        if decision.action == RecoveryAction.DEFER:
            return RecoveryGateResult(decision, False, decision.reason)

        if decision.action == RecoveryAction.REROUTE:
            return RecoveryGateResult(decision, True, "reroute is explicitly authorized for this recovery")

        if decision.action == RecoveryAction.RESUME:
            return RecoveryGateResult(decision, True, "queued work is eligible to resume")

        retry_decision = self.retry_policy.decide(
            attempt=state.attempt_count + 1,
            success=False,
            retryable=retryable,
        )
        return RecoveryGateResult(decision, retry_decision.retry, retry_decision.reason)
