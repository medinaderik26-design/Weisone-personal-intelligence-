"""PI-063 durable, versioned recovery snapshots."""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from .recovery_snapshot import RecoverySnapshot


class SQLiteRecoverySnapshotStore:
    """Persist validated recovery snapshots as immutable versions."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS recovery_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                snapshot_json TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                UNIQUE(task_id, version)
            )"""
        )
        self.connection.commit()

    def save(self, snapshot: RecoverySnapshot) -> int:
        snapshot.validate()
        row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) FROM recovery_snapshot WHERE task_id = ?",
            (snapshot.task_id,),
        ).fetchone()
        version = int(row[0]) + 1
        payload = {
            "task_id": snapshot.task_id,
            "work_state": asdict(snapshot.work_state),
            "latest_ledger": asdict(snapshot.latest_ledger) if snapshot.latest_ledger else None,
            "latest_reconciliation": asdict(snapshot.latest_reconciliation) if snapshot.latest_reconciliation else None,
            "decision": asdict(snapshot.decision),
        }
        self.connection.execute(
            "INSERT INTO recovery_snapshot (task_id, version, snapshot_json, recorded_at) VALUES (?, ?, ?, ?)",
            (snapshot.task_id, version, json.dumps(payload, default=str), datetime.now(timezone.utc).isoformat()),
        )
        self.connection.commit()
        return version

    def versions(self, task_id: str) -> tuple[int, ...]:
        rows = self.connection.execute(
            "SELECT version FROM recovery_snapshot WHERE task_id = ? ORDER BY version",
            (task_id,),
        ).fetchall()
        return tuple(row[0] for row in rows)

    def latest_json(self, task_id: str) -> Optional[str]:
        row = self.connection.execute(
            "SELECT snapshot_json FROM recovery_snapshot WHERE task_id = ? ORDER BY version DESC LIMIT 1",
            (task_id,),
        ).fetchone()
        return None if row is None else row[0]

    def close(self) -> None:
        self.connection.close()
