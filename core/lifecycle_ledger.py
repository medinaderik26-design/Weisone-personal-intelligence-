"""PI-057 ledger boundary that enforces lifecycle transitions on append."""

from .action_ledger import ActionLedger, ActionLedgerEntry
from .ledger_lifecycle import LedgerLifecycleValidator


class LifecycleActionLedger:
    """Action ledger facade that rejects contradictory stage transitions."""

    def __init__(self, ledger: ActionLedger | None = None, validator: LedgerLifecycleValidator | None = None) -> None:
        self.ledger = ledger or ActionLedger()
        self.validator = validator or LedgerLifecycleValidator()

    def append(self, entry: ActionLedgerEntry) -> None:
        existing = self.ledger.for_task(entry.task_id)
        if existing:
            last = existing[-1]
            if last.intent_id != entry.intent_id:
                raise ValueError("ledger intent changed within the same task")
            if last.operation != entry.operation or last.target != entry.target:
                raise ValueError("ledger action identity changed within the same task")
            self.validator.require(last.stage, entry.stage)
        self.ledger.append(entry)

    def record(self, **kwargs) -> ActionLedgerEntry:
        entry = ActionLedgerEntry.create(**kwargs) if hasattr(ActionLedgerEntry, "create") else ActionLedgerEntry(**kwargs)
        self.append(entry)
        return entry

    def for_task(self, task_id: str):
        return self.ledger.for_task(task_id)

    def for_intent(self, intent_id: str):
        return self.ledger.for_intent(intent_id)

    def all(self):
        return self.ledger.all()
