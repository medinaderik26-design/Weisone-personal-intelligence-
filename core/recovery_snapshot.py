"""PI-062 unified recovery snapshots."""

from dataclasses import dataclass
from typing import Optional

from .action_ledger import ActionLedgerEntry
from .ledger_recovery import LedgerRecoveryDecision
from .persistent_work_state import WorkState
from .reconciliation_record import ReconciliationRecord


@dataclass(frozen=True)
class RecoverySnapshot:
    task_id: str
    work_state: WorkState
    latest_ledger: Optional[ActionLedgerEntry]
    latest_reconciliation: Optional[ReconciliationRecord]
    decision: LedgerRecoveryDecision

    def validate(self) -> None:
        self.work_state.validate()
        if self.task_id != self.work_state.task_id:
            raise ValueError("snapshot task_id does not match work state")
        if self.latest_ledger is not None and self.latest_ledger.task_id != self.task_id:
            raise ValueError("ledger entry task_id does not match snapshot")
        if self.latest_reconciliation is not None and self.latest_reconciliation.task_id != self.task_id:
            raise ValueError("reconciliation task_id does not match snapshot")
        if self.decision.task_id != self.task_id:
            raise ValueError("recovery decision task_id does not match snapshot")


class RecoverySnapshotBuilder:
    def build(
        self,
        state: WorkState,
        decision: LedgerRecoveryDecision,
        *,
        ledger_entry: Optional[ActionLedgerEntry] = None,
        reconciliation: Optional[ReconciliationRecord] = None,
    ) -> RecoverySnapshot:
        snapshot = RecoverySnapshot(
            task_id=state.task_id,
            work_state=state,
            latest_ledger=ledger_entry,
            latest_reconciliation=reconciliation,
            decision=decision,
        )
        snapshot.validate()
        return snapshot
