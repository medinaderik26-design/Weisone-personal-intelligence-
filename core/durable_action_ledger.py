"""PI-058 SQLite-backed action ledger with lifecycle enforcement."""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from .action_ledger import ActionLedgerEntry
from .ledger_lifecycle import LedgerLifecycleValidator


class SQLiteActionLedger:
    """Durable local ledger; stores metadata, never sensitive payloads."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS action_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                intent_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                target TEXT NOT NULL,
                stage TEXT NOT NULL,
                statement TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence REAL
            )"""
        )
        self._conn.commit()
        self.validator = LedgerLifecycleValidator()

    def append(self, entry: ActionLedgerEntry) -> None:
        entry.validate()
        previous = self._conn.execute(
            "SELECT intent_id, operation, target, stage FROM action_ledger WHERE task_id = ? ORDER BY id DESC LIMIT 1",
            (entry.task_id,),
        ).fetchone()
        if previous:
            intent_id, operation, target, stage = previous
            if intent_id != entry.intent_id:
                raise ValueError("ledger intent changed within the same task")
            if operation != entry.operation or target != entry.target:
                raise ValueError("ledger action identity changed within the same task")
            self.validator.require(stage, entry.stage)

        self._conn.execute(
            """INSERT INTO action_ledger
            (task_id, intent_id, operation, target, stage, statement, timestamp, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.task_id,
                entry.intent_id,
                entry.operation,
                entry.target,
                entry.stage,
                entry.statement,
                entry.timestamp.isoformat(),
                entry.confidence,
            ),
        )
        self._conn.commit()

    def for_task(self, task_id: str) -> tuple[ActionLedgerEntry, ...]:
        rows = self._conn.execute(
            "SELECT task_id, intent_id, operation, target, stage, statement, timestamp, confidence FROM action_ledger WHERE task_id = ? ORDER BY id",
            (task_id,),
        ).fetchall()
        return tuple(self._entry(row) for row in rows)

    def for_intent(self, intent_id: str) -> tuple[ActionLedgerEntry, ...]:
        rows = self._conn.execute(
            "SELECT task_id, intent_id, operation, target, stage, statement, timestamp, confidence FROM action_ledger WHERE intent_id = ? ORDER BY id",
            (intent_id,),
        ).fetchall()
        return tuple(self._entry(row) for row in rows)

    def all(self) -> tuple[ActionLedgerEntry, ...]:
        rows = self._conn.execute(
            "SELECT task_id, intent_id, operation, target, stage, statement, timestamp, confidence FROM action_ledger ORDER BY id"
        ).fetchall()
        return tuple(self._entry(row) for row in rows)

    @staticmethod
    def _entry(row) -> ActionLedgerEntry:
        task_id, intent_id, operation, target, stage, statement, timestamp, confidence = row
        return ActionLedgerEntry(
            task_id=task_id,
            intent_id=intent_id,
            operation=operation,
            target=target,
            stage=stage,
            statement=statement,
            timestamp=datetime.fromisoformat(timestamp),
            confidence=confidence,
        )

    def close(self) -> None:
        self._conn.close()
