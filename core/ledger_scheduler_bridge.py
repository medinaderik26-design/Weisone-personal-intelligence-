"""PI-075 bridge scheduler receipts into the Action Ledger."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .action_ledger import ActionLedgerEntry
from .scheduler_receipt import SchedulerReceipt


@dataclass(frozen=True)
class LedgerSchedulerBridge:
    """Translate scheduler evidence into ledger stages without claiming execution."""

    def entry_from_receipt(self, receipt: SchedulerReceipt, operation: str, target: str) -> ActionLedgerEntry:
        receipt.validate()
        if not operation:
            raise ValueError("operation is required")
        if not target:
            raise ValueError("target is required")
        stage = receipt.state
        statement = (
            "Scheduler acknowledged handoff for this execution intent."
            if stage == "handed_off"
            else "Scheduler accepted this execution intent; execution outcome remains unconfirmed."
        )
        return ActionLedgerEntry(
            task_id=receipt.task_id,
            intent_id=receipt.intent_id,
            operation=operation,
            target=target,
            stage=stage,
            statement=statement,
            timestamp=datetime.fromisoformat(receipt.recorded_at),
        )
