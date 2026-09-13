"""PI-021 durable local work-state adapter.

Uses SQLite so unfinished work can survive process restarts without adding a
remote dependency. The schema stores only the work-state contract.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

from .persistent_work_state import WorkState


class SQLiteWorkStateStore:
    def __init__(self, path: str = "pi_work_state.db") -> None:
        self.path = Path(path)
        self._connection = sqlite3.connect(self.path)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS work_state (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                attempt_count INTEGER NOT NULL,
                provider TEXT,
                last_error TEXT,
                result_reference TEXT,
                metadata TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def save(self, state: WorkState) -> None:
        state.validate()
        self._connection.execute(
            """
            INSERT INTO work_state
              (task_id, status, attempt_count, provider, last_error,
               result_reference, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
              status=excluded.status,
              attempt_count=excluded.attempt_count,
              provider=excluded.provider,
              last_error=excluded.last_error,
              result_reference=excluded.result_reference,
              metadata=excluded.metadata
            """,
            (
                state.task_id,
                state.status,
                state.attempt_count,
                state.provider,
                state.last_error,
                state.result_reference,
                json.dumps(state.metadata),
            ),
        )
        self._connection.commit()

    def get(self, task_id: str) -> Optional[WorkState]:
        row = self._connection.execute(
            "SELECT task_id, status, attempt_count, provider, last_error, result_reference, metadata "
            "FROM work_state WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        return WorkState(
            task_id=row[0],
            status=row[1],
            attempt_count=row[2],
            provider=row[3],
            last_error=row[4],
            result_reference=row[5],
            metadata=json.loads(row[6]),
        )

    def unfinished(self):
        rows = self._connection.execute(
            "SELECT task_id, status, attempt_count, provider, last_error, result_reference, metadata "
            "FROM work_state WHERE status IN ('queued', 'running') ORDER BY rowid"
        ).fetchall()
        return [
            WorkState(
                task_id=row[0], status=row[1], attempt_count=row[2], provider=row[3],
                last_error=row[4], result_reference=row[5], metadata=json.loads(row[6])
            )
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()
