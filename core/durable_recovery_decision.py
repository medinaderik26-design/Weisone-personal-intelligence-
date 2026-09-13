"""PI-067 durable recovery execution-boundary decisions."""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class DurableRecoveryDecision:
    task_id: str
    classification: str
    action: str
    reason: str
    recorded_at: str

    @classmethod
    def create(cls, task_id: str, classification: str, action: str, reason: str, now: Optional[datetime] = None):
        if not task_id:
            raise ValueError("task_id is required")
        if not classification:
            raise ValueError("classification is required")
        if not action:
            raise ValueError("action is required")
        if not reason:
            raise ValueError("reason is required")
        timestamp = now or datetime.now(timezone.utc)
        return cls(task_id, classification, action, reason, timestamp.isoformat())

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.classification:
            raise ValueError("classification is required")
        if not self.action:
            raise ValueError("action is required")
        if not self.reason:
            raise ValueError("reason is required")
        if not self.recorded_at:
            raise ValueError("recorded_at is required")


class SQLiteRecoveryDecisionLog:
    """Durably record recovery-boundary decisions without sensitive payloads."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS recovery_decision (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                classification TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def append(self, decision: DurableRecoveryDecision) -> int:
        decision.validate()
        payload = json.dumps(asdict(decision), sort_keys=True)
        cursor = self.connection.execute(
            "INSERT INTO recovery_decision (task_id, classification, action, reason, recorded_at, payload) VALUES (?, ?, ?, ?, ?, ?)",
            (decision.task_id, decision.classification, decision.action, decision.reason, decision.recorded_at, payload),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def for_task(self, task_id: str) -> tuple[DurableRecoveryDecision, ...]:
        rows = self.connection.execute(
            "SELECT task_id, classification, action, reason, recorded_at FROM recovery_decision WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return tuple(DurableRecoveryDecision(*row) for row in rows)

    def all(self) -> tuple[DurableRecoveryDecision, ...]:
        rows = self.connection.execute(
            "SELECT task_id, classification, action, reason, recorded_at FROM recovery_decision ORDER BY id"
        ).fetchall()
        return tuple(DurableRecoveryDecision(*row) for row in rows)

    def close(self) -> None:
        self.connection.close()
