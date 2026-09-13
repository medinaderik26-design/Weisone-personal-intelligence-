"""PI-055 durable-style action ledger for accountable agent history."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class ActionLedgerEntry:
    task_id: str
    intent_id: str
    operation: str
    target: str
    stage: str
    statement: str
    timestamp: datetime
    confidence: Optional[float] = None

    def validate(self) -> None:
        required = (self.task_id, self.intent_id, self.operation, self.target, self.stage, self.statement)
        if any(not value for value in required):
            raise ValueError("ledger identity and statement fields are required")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class ActionLedger:
    """Append-only reference ledger. Sensitive payloads are intentionally excluded."""

    def __init__(self) -> None:
        self._entries: list[ActionLedgerEntry] = []

    def append(self, entry: ActionLedgerEntry) -> None:
        entry.validate()
        self._entries.append(entry)

    def record(
        self,
        *,
        task_id: str,
        intent_id: str,
        operation: str,
        target: str,
        stage: str,
        statement: str,
        confidence: Optional[float] = None,
    ) -> ActionLedgerEntry:
        entry = ActionLedgerEntry(
            task_id=task_id,
            intent_id=intent_id,
            operation=operation,
            target=target,
            stage=stage,
            statement=statement,
            timestamp=datetime.now(timezone.utc),
            confidence=confidence,
        )
        self.append(entry)
        return entry

    def for_task(self, task_id: str) -> tuple[ActionLedgerEntry, ...]:
        return tuple(entry for entry in self._entries if entry.task_id == task_id)

    def for_intent(self, intent_id: str) -> tuple[ActionLedgerEntry, ...]:
        return tuple(entry for entry in self._entries if entry.intent_id == intent_id)

    def all(self) -> tuple[ActionLedgerEntry, ...]:
        return tuple(self._entries)
