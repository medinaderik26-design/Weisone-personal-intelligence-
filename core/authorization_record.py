"""PI-039 explainable authorization decision records."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass(frozen=True)
class AuthorizationDecisionRecord:
    task_id: str
    subject: str
    provider: str
    task_type: str
    allowed: bool
    reason: str
    timestamp: datetime
    fields_allowed: tuple[str, ...] = ()
    fields_denied: tuple[str, ...] = ()
    policy_sources: tuple[str, ...] = ()
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        task_id: str,
        subject: str,
        provider: str,
        task_type: str,
        allowed: bool,
        reason: str,
        fields_allowed: tuple[str, ...] = (),
        fields_denied: tuple[str, ...] = (),
        policy_sources: tuple[str, ...] = (),
        metadata: Optional[Dict[str, str]] = None,
    ) -> "AuthorizationDecisionRecord":
        if not task_id or not subject or not provider or not task_type:
            raise ValueError("task identity fields are required")
        if not reason:
            raise ValueError("reason is required")
        return cls(
            task_id=task_id,
            subject=subject,
            provider=provider,
            task_type=task_type,
            allowed=allowed,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
            fields_allowed=fields_allowed,
            fields_denied=fields_denied,
            policy_sources=policy_sources,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "subject": self.subject,
            "provider": self.provider,
            "task_type": self.task_type,
            "allowed": self.allowed,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "fields_allowed": self.fields_allowed,
            "fields_denied": self.fields_denied,
            "policy_sources": self.policy_sources,
            "metadata": self.metadata,
        }


class AuthorizationDecisionLog:
    """Append-only in-memory decision log for the reference implementation."""

    def __init__(self) -> None:
        self._records: list[AuthorizationDecisionRecord] = []

    def append(self, record: AuthorizationDecisionRecord) -> None:
        self._records.append(record)

    def all(self) -> tuple[AuthorizationDecisionRecord, ...]:
        return tuple(self._records)

    def for_task(self, task_id: str) -> tuple[AuthorizationDecisionRecord, ...]:
        return tuple(record for record in self._records if record.task_id == task_id)
