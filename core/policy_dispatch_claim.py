"""PI-085 durable claim adapter for policy-approved dispatch requests."""

from dataclasses import dataclass
from typing import Optional

from .durable_recovery_dispatch import DispatchClaim, SQLiteRecoveryDispatchStore
from .policy_dispatch_bridge import PolicyDispatchRequest


@dataclass(frozen=True)
class PolicyDispatchClaimResult:
    task_id: str
    dispatch_key: Optional[str]
    claimed: bool
    reason: str
    claim: Optional[DispatchClaim] = None


class PolicyDispatchClaimAdapter:
    """Turn an eligible policy dispatch request into one durable claim.

    This adapter is the handoff between policy eligibility and durable
    scheduler-facing idempotency. It does not execute work or authorize
    external side effects.
    """

    def __init__(self, store: SQLiteRecoveryDispatchStore) -> None:
        self.store = store

    def claim(self, request: PolicyDispatchRequest, now=None) -> PolicyDispatchClaimResult:
        if not request.task_id:
            raise ValueError("task_id is required")
        if not request.action:
            raise ValueError("action is required")

        if not request.eligible or not request.dispatch_key:
            return PolicyDispatchClaimResult(
                task_id=request.task_id,
                dispatch_key=request.dispatch_key,
                claimed=False,
                reason="policy dispatch request is not eligible for a durable claim",
            )

        claim = self.store.claim(
            request.task_id,
            request.classification,
            request.action,
            now=now,
        )

        if claim is None:
            return PolicyDispatchClaimResult(
                task_id=request.task_id,
                dispatch_key=request.dispatch_key,
                claimed=False,
                reason="durable dispatch claim already exists for this logical recovery action",
            )

        if claim.dispatch_key != request.dispatch_key:
            raise ValueError("durable claim key does not match policy dispatch request")

        return PolicyDispatchClaimResult(
            task_id=request.task_id,
            dispatch_key=request.dispatch_key,
            claimed=True,
            reason="policy-approved dispatch was durably claimed",
            claim=claim,
        )
