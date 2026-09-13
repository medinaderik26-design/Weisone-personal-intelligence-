"""PI-060 explicit recovery reconciliation records."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .ledger_recovery import LedgerRecoveryDecision
from .persistent_work_state import WorkState


@dataclass(frozen=True)
class ReconciliationRecord:
    task_id: str
    intent_id: Optional[str]
    prior_status: str
    ledger_stage: Optional[str]
    recovery_action: str
    reason: str
    recorded_at: datetime

    @classmethod
    def from_decision(
        cls,
        state: WorkState,
        decision: LedgerRecoveryDecision,
        *,
        now: Optional[datetime] = None,
    ) -> "ReconciliationRecord":
        return cls(
            task_id=state.task_id,
            intent_id=decision.intent_id,
            prior_status=state.status,
            ledger_stage=decision.current_stage,
            recovery_action=decision.action,
            reason=decision.reason,
            recorded_at=now or datetime.now(timezone.utc),
        )

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.prior_status:
            raise ValueError("prior_status is required")
        if not self.recovery_action:
            raise ValueError("recovery_action is required")
        if not self.reason:
            raise ValueError("reason is required")


class ReconciliationLog:
    """Append-only reference log for recovery decisions."""

    def __init__(self) -> None:
        self._records: list[ReconciliationRecord] = []

    def append(self, record: ReconciliationRecord) -> None:
        record.validate()
        self._records.append(record)

    def for_task(self, task_id: str) -> tuple[ReconciliationRecord, ...]:
        return tuple(r for r in self._records if r.task_id == task_id)

    def all(self) -> tuple[ReconciliationRecord, ...]:
        return tuple(self._records)
