"""PI-038 consent and revocation controls."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass(frozen=True)
class ConsentGrant:
    subject: str
    provider: str
    task_type: str
    granted_at: datetime
    expires_at: Optional[datetime] = None

    def active(self, now: Optional[datetime] = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return self.expires_at is None or current < self.expires_at


class ConsentRegistry:
    """Explicit, revocable provider consent registry."""

    def __init__(self) -> None:
        self._grants: Dict[tuple[str, str, str], ConsentGrant] = {}

    def grant(self, subject: str, provider: str, task_type: str, *, expires_at: Optional[datetime] = None, now: Optional[datetime] = None) -> ConsentGrant:
        if not subject or not provider or not task_type:
            raise ValueError("subject, provider, and task_type are required")
        current = now or datetime.now(timezone.utc)
        grant = ConsentGrant(subject, provider, task_type, current, expires_at)
        self._grants[(subject, provider, task_type)] = grant
        return grant

    def revoke(self, subject: str, provider: str, task_type: str) -> None:
        self._grants.pop((subject, provider, task_type), None)

    def permits(self, subject: str, provider: str, task_type: str, *, now: Optional[datetime] = None) -> bool:
        grant = self._grants.get((subject, provider, task_type))
        return grant is not None and grant.active(now)

    def get(self, subject: str, provider: str, task_type: str) -> Optional[ConsentGrant]:
        return self._grants.get((subject, provider, task_type))
