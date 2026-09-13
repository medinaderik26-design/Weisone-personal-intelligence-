"""PI-061 durable reconciliation history linked to action intent."""

import sqlite3
from datetime import datetime
from typing import Optional

from .reconciliation_record import ReconciliationRecord


class SQLiteReconciliationLog:
    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS reconciliation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                intent_id TEXT,
                prior_status TEXT NOT NULL,
                ledger_stage TEXT,
                recovery_action TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )"""
        )
        self.connection.commit()

    def append(self, record: ReconciliationRecord) -> None:
        record.validate()
        self.connection.execute(
            """INSERT INTO reconciliation
            (task_id, intent_id, prior_status, ledger_stage, recovery_action, reason, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                record.task_id,
                record.intent_id,
                record.prior_status,
                record.ledger_stage,
                record.recovery_action,
                record.reason,
                record.recorded_at.isoformat(),
            ),
        )
        self.connection.commit()

    def for_task(self, task_id: str) -> tuple[ReconciliationRecord, ...]:
        rows = self.connection.execute(
            "SELECT task_id, intent_id, prior_status, ledger_stage, recovery_action, reason, recorded_at "
            "FROM reconciliation WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return tuple(
            ReconciliationRecord(
                task_id=row[0],
                intent_id=row[1],
                prior_status=row[2],
                ledger_stage=row[3],
                recovery_action=row[4],
                reason=row[5],
                recorded_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        )

    def all(self) -> tuple[ReconciliationRecord, ...]:
        rows = self.connection.execute(
            "SELECT task_id, intent_id, prior_status, ledger_stage, recovery_action, reason, recorded_at "
            "FROM reconciliation ORDER BY id"
        ).fetchall()
        return tuple(
            ReconciliationRecord(
                task_id=row[0],
                intent_id=row[1],
                prior_status=row[2],
                ledger_stage=row[3],
                recovery_action=row[4],
                reason=row[5],
                recorded_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        )

    def close(self) -> None:
        self.connection.close()
