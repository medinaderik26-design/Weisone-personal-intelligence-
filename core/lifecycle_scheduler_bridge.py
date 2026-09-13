"""PI-077 lifecycle-aware scheduler-to-ledger bridge."""

from dataclasses import dataclass
from datetime import datetime

from .action_ledger import ActionLedgerEntry
from .ledger_scheduler_validator import SchedulerLedgerValidator
from .scheduler_receipt import SchedulerReceipt


@dataclass(frozen=True)
class LifecycleSchedulerBridge:
    """Convert scheduler receipts into ledger entries only after validation."""

    validator: SchedulerLedgerValidator = SchedulerLedgerValidator()

    def entry_from_receipt(
        self,
        receipt: SchedulerReceipt,
        operation: str,
        target: str,
        prior_stages: tuple[str, ...],
    ) -> ActionLedgerEntry:
        receipt.validate()
        if not operation:
            raise ValueError("operation is required")
        if not target:
            raise ValueError("target is required")

        self.validator.require(prior_stages, receipt.state)

        statement = (
            "Scheduler acknowledged handoff for this execution intent."
            if receipt.state == "handed_off"
            else "Scheduler accepted this execution intent; execution outcome remains unconfirmed."
        )
        return ActionLedgerEntry(
            task_id=receipt.task_id,
            intent_id=receipt.intent_id,
            operation=operation,
            target=target,
            stage=receipt.state,
            statement=statement,
            timestamp=datetime.fromisoformat(receipt.recorded_at),
        )
