"""PI-020 durable work-state contracts.

Keeps queued and executing work recoverable across process restarts without
coupling the core to a particular database or storage provider.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class WorkState:
    task_id: str
    status: str = "queued"
    attempt_count: int = 0
    provider: Optional[str] = None
    last_error: Optional[str] = None
    result_reference: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if self.status not in {"queued", "running", "completed", "failed"}:
            raise ValueError("invalid work status")
        if self.attempt_count < 0:
            raise ValueError("attempt_count cannot be negative")


class InMemoryWorkStateStore:
    """Reference store; replaceable by a durable adapter later."""

    def __init__(self) -> None:
        self._states: Dict[str, WorkState] = {}

    def save(self, state: WorkState) -> None:
        state.validate()
        self._states[state.task_id] = state

    def get(self, task_id: str) -> Optional[WorkState]:
        return self._states.get(task_id)

    def remove(self, task_id: str) -> None:
        self._states.pop(task_id, None)
