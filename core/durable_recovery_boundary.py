"""PI-068 authoritative durable recovery-boundary record."""

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class RecoveryBoundaryRecord:
    task_id: str
    classification: str
    action: str
    reason: str
    boundary: str = "execution_boundary"
    recorded_at: str = ""

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
        return cls(task_id, classification, action, reason, "execution_boundary", (now or datetime.now(timezone.utc)).isoformat())

    def validate(self) -> None:
        for name in ("task_id", "classification", "action", "reason", "boundary", "recorded_at"):
            if not getattr(self, name):
                raise ValueError(f"{name} is required")
        if self.boundary != "execution_boundary":
            raise ValueError("invalid recovery boundary")


class SQLiteRecoveryBoundaryLog:
    """Append-only durable record of decisions crossing the execution boundary."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS recovery_boundary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                classification TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                boundary TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def record(self, decision: RecoveryBoundaryRecord) -> int:
        decision.validate()
        payload = json.dumps(asdict(decision), sort_keys=True)
        cursor = self.connection.execute(
            "INSERT INTO recovery_boundary (task_id, classification, action, reason, boundary, recorded_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (decision.task_id, decision.classification, decision.action, decision.reason, decision.boundary, decision.recorded_at, payload),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def for_task(self, task_id: str) -> tuple[RecoveryBoundaryRecord, ...]:
        rows = self.connection.execute(
            "SELECT task_id, classification, action, reason, boundary, recorded_at FROM recovery_boundary WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return tuple(RecoveryBoundaryRecord(*row) for row in rows)

    def close(self) -> None:
        self.connection.close()
