"""PI-086 durable dispatch-claim to scheduler-handoff boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .policy_dispatch_claim import PolicyDispatchClaimResult
from .scheduler_receipt import SQLiteSchedulerReceiptStore, SchedulerReceipt


@dataclass(frozen=True)
class SchedulerHandoffRequest:
    task_id: str
    dispatch_key: str
    intent_id: str
    eligible: bool
    reason: str


class DurableClaimHandoff:
    """Translate a durable claim into a scheduler handoff request.

    This layer never calls the scheduler. It creates a bounded request that
    may be handed to a scheduler adapter. Scheduler acknowledgement remains
    separate evidence.
    """

    def __init__(self, receipts: SQLiteSchedulerReceiptStore) -> None:
        self.receipts = receipts

    def prepare(
        self,
        claim_result: PolicyDispatchClaimResult,
        *,
        intent_id: Optional[str] = None,
    ) -> SchedulerHandoffRequest:
        if not claim_result.task_id:
            raise ValueError("task_id is required")

        if not claim_result.claimed or claim_result.claim is None:
            return SchedulerHandoffRequest(
                task_id=claim_result.task_id,
                dispatch_key=claim_result.dispatch_key or "",
                intent_id=intent_id or "",
                eligible=False,
                reason="no new durable claim exists; scheduler handoff is not permitted",
            )

        if not intent_id:
            raise ValueError("intent_id is required for scheduler handoff")

        if claim_result.claim.task_id != claim_result.task_id:
            raise ValueError("claim task identity does not match result task identity")

        if claim_result.claim.dispatch_key != claim_result.dispatch_key:
            raise ValueError("claim dispatch identity does not match result")

        return SchedulerHandoffRequest(
            task_id=claim_result.task_id,
            dispatch_key=claim_result.claim.dispatch_key,
            intent_id=intent_id,
            eligible=True,
            reason="durable claim permits scheduler handoff request",
        )

    def record_handoff(self, request: SchedulerHandoffRequest, now=None) -> SchedulerReceipt:
        if not request.eligible:
            raise PermissionError("scheduler handoff is not eligible")
        if not request.task_id or not request.dispatch_key or not request.intent_id:
            raise ValueError("task_id, dispatch_key, and intent_id are required")

        timestamp = now or datetime.now(timezone.utc)
        receipt = SchedulerReceipt(
            task_id=request.task_id,
            intent_id=request.intent_id,
            dispatch_key=request.dispatch_key,
            state="handed_off",
            recorded_at=timestamp.isoformat(),
        )
        self.receipts.record(receipt)
        return self.receipts.get(request.dispatch_key) or receipt
