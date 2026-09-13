"""PI-088 scheduler acceptance -> execution start boundary."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .scheduler_acceptance import SchedulerAcceptanceResult


@dataclass(frozen=True)
class ExecutionStartRecord:
    task_id: str
    dispatch_key: str
    intent_id: str
    started: bool
    recorded_at: str
    reason: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.dispatch_key:
            raise ValueError("dispatch_key is required")
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if not self.recorded_at:
            raise ValueError("recorded_at is required")


class ExecutionStartBoundary:
    """Translate scheduler acceptance into explicit execution-start evidence."""

    def start(self, acceptance: SchedulerAcceptanceResult, now=None) -> ExecutionStartRecord:
        if not acceptance.task_id:
            raise ValueError("task_id is required")
        if not acceptance.dispatch_key:
            raise ValueError("dispatch_key is required")
        if not acceptance.intent_id:
            raise ValueError("intent_id is required")

        timestamp = now or datetime.now(timezone.utc)

        if not acceptance.accepted:
            record = ExecutionStartRecord(
                task_id=acceptance.task_id,
                dispatch_key=acceptance.dispatch_key,
                intent_id=acceptance.intent_id,
                started=False,
                recorded_at=timestamp.isoformat(),
                reason="execution cannot start because scheduler acceptance was not confirmed",
            )
            record.validate()
            return record

        record = ExecutionStartRecord(
            task_id=acceptance.task_id,
            dispatch_key=acceptance.dispatch_key,
            intent_id=acceptance.intent_id,
            started=True,
            recorded_at=timestamp.isoformat(),
            reason="scheduler acceptance permits execution to begin",
        )
        record.validate()
        return record
