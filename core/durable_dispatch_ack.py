"""PI-072 durable, idempotent scheduler acknowledgement state."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


ACK_STATES = {"claimed", "handed_off", "accepted"}


@dataclass(frozen=True)
class DispatchAcknowledgement:
    task_id: str
    dispatch_key: str
    state: str
    recorded_at: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.dispatch_key:
            raise ValueError("dispatch_key is required")
        if self.state not in ACK_STATES:
            raise ValueError("invalid acknowledgement state")
        if not self.recorded_at:
            raise ValueError("recorded_at is required")


class SQLiteDispatchAcknowledgementStore:
    """Persist scheduler acknowledgement state across restarts."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS dispatch_ack (
                dispatch_key TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                state TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def record(self, ack: DispatchAcknowledgement) -> None:
        ack.validate()
        existing = self.get(ack.dispatch_key)
        if existing is not None:
            order = {"claimed": 0, "handed_off": 1, "accepted": 2}
            if existing.task_id != ack.task_id:
                raise ValueError("dispatch key is bound to a different task")
            if order[ack.state] < order[existing.state]:
                raise ValueError("acknowledgement state cannot move backward")
            if ack.state == existing.state:
                return
        self.connection.execute(
            "INSERT INTO dispatch_ack (dispatch_key, task_id, state, recorded_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(dispatch_key) DO UPDATE SET state = excluded.state, recorded_at = excluded.recorded_at",
            (ack.dispatch_key, ack.task_id, ack.state, ack.recorded_at),
        )
        self.connection.commit()

    def get(self, dispatch_key: str) -> Optional[DispatchAcknowledgement]:
        row = self.connection.execute(
            "SELECT task_id, dispatch_key, state, recorded_at FROM dispatch_ack WHERE dispatch_key = ?",
            (dispatch_key,),
        ).fetchone()
        return None if row is None else DispatchAcknowledgement(*row)

    def close(self) -> None:
        self.connection.close()
