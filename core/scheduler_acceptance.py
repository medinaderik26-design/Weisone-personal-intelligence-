"""PI-087 scheduler handoff -> scheduler acceptance boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .durable_claim_handoff import SchedulerHandoffRequest
from .scheduler_receipt import SQLiteSchedulerReceiptStore, SchedulerReceipt


@dataclass(frozen=True)
class SchedulerAcceptanceResult:
    task_id: str
    dispatch_key: str
    intent_id: str
    accepted: bool
    reason: str
    receipt: Optional[SchedulerReceipt] = None


class SchedulerAcceptanceBoundary:
    """Record scheduler acceptance without claiming execution occurred."""

    def __init__(self, receipts: SQLiteSchedulerReceiptStore) -> None:
        self.receipts = receipts

    def accept(self, request: SchedulerHandoffRequest, now=None) -> SchedulerAcceptanceResult:
        if not request.task_id:
            raise ValueError("task_id is required")
        if not request.dispatch_key:
            raise ValueError("dispatch_key is required")
        if not request.intent_id:
            raise ValueError("intent_id is required")
        if not request.eligible:
            return SchedulerAcceptanceResult(
                request.task_id,
                request.dispatch_key,
                request.intent_id,
                False,
                "scheduler acceptance is blocked because handoff is not eligible",
            )

        existing = self.receipts.get(request.dispatch_key)
        if existing is not None:
            if existing.task_id != request.task_id or existing.intent_id != request.intent_id:
                raise ValueError("scheduler receipt identity changed")
            if existing.state == "accepted":
                return SchedulerAcceptanceResult(
                    request.task_id,
                    request.dispatch_key,
                    request.intent_id,
                    True,
                    "scheduler acceptance was already durably recorded",
                    existing,
                )
            if existing.state != "handed_off":
                raise ValueError("invalid scheduler receipt state for acceptance")
        else:
            raise ValueError("scheduler handoff receipt is required before acceptance")

        timestamp = now or datetime.now(timezone.utc)
        receipt = SchedulerReceipt(
            task_id=request.task_id,
            intent_id=request.intent_id,
            dispatch_key=request.dispatch_key,
            state="accepted",
            recorded_at=timestamp.isoformat(),
        )
        self.receipts.record(receipt)
        stored = self.receipts.get(request.dispatch_key) or receipt
        return SchedulerAcceptanceResult(
            request.task_id,
            request.dispatch_key,
            request.intent_id,
            True,
            "scheduler acceptance was durably recorded",
            stored,
        )
