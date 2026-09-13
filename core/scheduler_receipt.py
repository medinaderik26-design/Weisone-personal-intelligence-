"""PI-074 durable scheduler boundary receipts."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

RECEIPT_STATES = {"handed_off", "accepted"}


@dataclass(frozen=True)
class SchedulerReceipt:
    task_id: str
    intent_id: str
    dispatch_key: str
    state: str
    recorded_at: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.intent_id:
            raise ValueError("intent_id is required")
        if not self.dispatch_key:
            raise ValueError("dispatch_key is required")
        if self.state not in RECEIPT_STATES:
            raise ValueError("invalid scheduler receipt state")
        if not self.recorded_at:
            raise ValueError("recorded_at is required")


class SQLiteSchedulerReceiptStore:
    """Persist scheduler handoff/acceptance evidence without sensitive payloads."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS scheduler_receipt (
                dispatch_key TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                intent_id TEXT NOT NULL,
                state TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def record(self, receipt: SchedulerReceipt) -> None:
        receipt.validate()
        existing = self.get(receipt.dispatch_key)
        order = {"handed_off": 0, "accepted": 1}
        if existing is not None:
            if existing.task_id != receipt.task_id or existing.intent_id != receipt.intent_id:
                raise ValueError("dispatch key identity changed")
            if order[receipt.state] < order[existing.state]:
                raise ValueError("scheduler receipt cannot move backward")
            if receipt.state == existing.state:
                return
        self.connection.execute(
            "INSERT INTO scheduler_receipt (dispatch_key, task_id, intent_id, state, recorded_at) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(dispatch_key) DO UPDATE SET state = excluded.state, recorded_at = excluded.recorded_at",
            (receipt.dispatch_key, receipt.task_id, receipt.intent_id, receipt.state, receipt.recorded_at),
        )
        self.connection.commit()

    def get(self, dispatch_key: str) -> Optional[SchedulerReceipt]:
        row = self.connection.execute(
            "SELECT task_id, intent_id, dispatch_key, state, recorded_at FROM scheduler_receipt WHERE dispatch_key = ?",
            (dispatch_key,),
        ).fetchone()
        return None if row is None else SchedulerReceipt(*row)

    def close(self) -> None:
        self.connection.close()
