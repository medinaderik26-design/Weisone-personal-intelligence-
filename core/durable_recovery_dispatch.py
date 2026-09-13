"""PI-070 durable recovery dispatch idempotency."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional


@dataclass(frozen=True)
class DispatchClaim:
    task_id: str
    dispatch_key: str
    action: str
    claimed_at: str


class SQLiteRecoveryDispatchStore:
    """Durably claim scheduler-facing recovery actions exactly once per key."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS recovery_dispatch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                dispatch_key TEXT NOT NULL UNIQUE,
                action TEXT NOT NULL,
                claimed_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    @staticmethod
    def make_key(task_id: str, classification: str, action: str) -> str:
        if not task_id or not classification or not action:
            raise ValueError("task_id, classification, and action are required")
        raw = f"{task_id}|{classification}|{action}".encode("utf-8")
        return sha256(raw).hexdigest()

    def claim(self, task_id: str, classification: str, action: str, now: Optional[datetime] = None) -> Optional[DispatchClaim]:
        key = self.make_key(task_id, classification, action)
        timestamp = (now or datetime.now(timezone.utc)).isoformat()
        try:
            self.connection.execute(
                "INSERT INTO recovery_dispatch (task_id, dispatch_key, action, claimed_at) VALUES (?, ?, ?, ?)",
                (task_id, key, action, timestamp),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            return None
        return DispatchClaim(task_id, key, action, timestamp)

    def has_claim(self, dispatch_key: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM recovery_dispatch WHERE dispatch_key = ? LIMIT 1",
            (dispatch_key,),
        ).fetchone()
        return row is not None

    def close(self) -> None:
        self.connection.close()
