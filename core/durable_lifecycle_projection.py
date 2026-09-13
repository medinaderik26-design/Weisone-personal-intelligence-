"""PI-079 durable, versioned lifecycle projections."""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from .lifecycle_projection import LifecycleProjection


class SQLiteLifecycleProjectionStore:
    """Persist immutable lifecycle projection versions across restarts."""

    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS lifecycle_projection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                projection_json TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                UNIQUE(task_id, version)
            )"""
        )
        self.connection.commit()

    def save(self, projection: LifecycleProjection) -> int:
        if not projection.task_id:
            raise ValueError("task_id is required")
        row = self.connection.execute(
            "SELECT COALESCE(MAX(version), 0) FROM lifecycle_projection WHERE task_id = ?",
            (projection.task_id,),
        ).fetchone()
        version = int(row[0]) + 1
        payload = asdict(projection)
        self.connection.execute(
            "INSERT INTO lifecycle_projection (task_id, version, projection_json, recorded_at) VALUES (?, ?, ?, ?)",
            (
                projection.task_id,
                version,
                json.dumps(payload, default=str),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.connection.commit()
        return version

    def versions(self, task_id: str) -> tuple[int, ...]:
        rows = self.connection.execute(
            "SELECT version FROM lifecycle_projection WHERE task_id = ? ORDER BY version",
            (task_id,),
        ).fetchall()
        return tuple(row[0] for row in rows)

    def latest_json(self, task_id: str) -> Optional[str]:
        row = self.connection.execute(
            "SELECT projection_json FROM lifecycle_projection WHERE task_id = ? ORDER BY version DESC LIMIT 1",
            (task_id,),
        ).fetchone()
        return None if row is None else row[0]

    def close(self) -> None:
        self.connection.close()
