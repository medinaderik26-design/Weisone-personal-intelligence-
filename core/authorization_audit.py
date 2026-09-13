"""PI-037 auditable authorization decisions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AuthorizationAuditEvent:
    task_id: str
    provider: str
    allowed: bool
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.provider:
            raise ValueError("provider is required")
        if not self.reason:
            raise ValueError("reason is required")


class AuthorizationAuditLog:
    """Append-only in-memory reference log for authorization decisions."""

    def __init__(self) -> None:
        self._events: List[AuthorizationAuditEvent] = []

    def record(self, event: AuthorizationAuditEvent) -> AuthorizationAuditEvent:
        event.validate()
        self._events.append(event)
        return event

    def all(self) -> List[AuthorizationAuditEvent]:
        return list(self._events)

    def for_task(self, task_id: str) -> List[AuthorizationAuditEvent]:
        return [event for event in self._events if event.task_id == task_id]

    def latest(self, task_id: str) -> Optional[AuthorizationAuditEvent]:
        events = self.for_task(task_id)
        return events[-1] if events else None
