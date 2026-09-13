"""PI-040 persistent-style revocation propagation contracts."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass(frozen=True)
class RevocationEvent:
    subject: str
    provider: str
    task_type: str
    revoked_at: datetime
    reason: str = "consent revoked"


class RevocationRegistry:
    """Reference registry for revocations visible to workers and queues."""

    def __init__(self) -> None:
        self._events: Dict[tuple[str, str, str], RevocationEvent] = {}

    def revoke(
        self,
        subject: str,
        provider: str,
        task_type: str,
        *,
        reason: str = "consent revoked",
        now: Optional[datetime] = None,
    ) -> RevocationEvent:
        if not subject or not provider or not task_type:
            raise ValueError("subject, provider, and task_type are required")
        if not reason:
            raise ValueError("reason is required")
        event = RevocationEvent(
            subject=subject,
            provider=provider,
            task_type=task_type,
            revoked_at=now or datetime.now(timezone.utc),
            reason=reason,
        )
        self._events[(subject, provider, task_type)] = event
        return event

    def is_revoked(self, subject: str, provider: str, task_type: str) -> bool:
        return (subject, provider, task_type) in self._events

    def get(self, subject: str, provider: str, task_type: str) -> Optional[RevocationEvent]:
        return self._events.get((subject, provider, task_type))


@dataclass(frozen=True)
class RevocationCheck:
    allowed: bool
    reason: str


class RevocationGuard:
    """Final lightweight check workers can apply before execution."""

    def __init__(self, registry: RevocationRegistry) -> None:
        self.registry = registry

    def check(self, subject: str, provider: str, task_type: str) -> RevocationCheck:
        event = self.registry.get(subject, provider, task_type)
        if event is not None:
            return RevocationCheck(False, event.reason)
        return RevocationCheck(True, "no matching revocation exists")
