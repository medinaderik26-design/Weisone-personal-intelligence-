"""PI-069 duplicate protection for scheduler-facing recovery decisions."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RecoveryDispatchKey:
    task_id: str
    classification: str
    action: str

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.classification:
            raise ValueError("classification is required")
        if not self.action:
            raise ValueError("action is required")


class RecoveryDispatchGuard:
    """Ensure one logical recovery decision is dispatched only once."""

    def __init__(self) -> None:
        self._dispatched: Dict[RecoveryDispatchKey, str] = {}

    def claim(self, key: RecoveryDispatchKey, boundary_record_id: int) -> bool:
        key.validate()
        if boundary_record_id <= 0:
            raise ValueError("boundary_record_id must be positive")
        if key in self._dispatched:
            return False
        self._dispatched[key] = str(boundary_record_id)
        return True

    def boundary_record_id(self, key: RecoveryDispatchKey) -> str | None:
        key.validate()
        return self._dispatched.get(key)
