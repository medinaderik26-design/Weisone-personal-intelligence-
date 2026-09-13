"""PI-082 durable projection-drift policy decisions."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DurableProjectionPolicyDecision:
    task_id: str
    classification: str
    action: str
    reason: str
    recorded_at: str

    @classmethod
    def create(cls, task_id: str, classification: str, action: str, reason: str, now=None):
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

    def validate(self):
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


class SQLiteProjectionDriftPolicyLog:
    """Persist immutable projection-drift policy decisions across restarts."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS projection_drift_policy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                classification TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def record(self, decision: DurableProjectionPolicyDecision) -> None:
        decision.validate()
        self.connection.execute(
            "INSERT INTO projection_drift_policy
             (task_id, classification, action, reason, recorded_at)
             VALUES (?, ?, ?, ?, ?)",
            (
                decision.task_id,
                decision.classification,
                decision.action,
                decision.reason,
                decision.recorded_at,
            ),
        )
        self.connection.commit()

    def for_task(self, task_id: str) -> tuple[DurableProjectionPolicyDecision, ...]:
        rows = self.connection.execute(
            "SELECT task_id, classification, action, reason, recorded_at
             FROM projection_drift_policy WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return tuple(DurableProjectionPolicyDecision(*row) for row in rows)

    def all(self) -> tuple[DurableProjectionPolicyDecision, ...]:
        rows = self.connection.execute(
            "SELECT task_id, classification, action, reason, recorded_at
             FROM projection_drift_policy ORDER BY id"
        ).fetchall()
        return tuple(DurableProjectionPolicyDecision(*row) for row in rows)

    def close(self) -> None:
        self.connection.close()
