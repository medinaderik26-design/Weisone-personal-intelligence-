"""PI-024 execution leases and heartbeats.

A lease distinguishes an actively maintained execution from work that may
have been abandoned after a worker or process failure.
"""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass(frozen=True)
class ExecutionLease:
    task_id: str
    owner_id: str
    acquired_at: datetime
    expires_at: datetime
    heartbeat_at: datetime

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.owner_id:
            raise ValueError("owner_id is required")
        if self.expires_at < self.acquired_at:
            raise ValueError("expires_at cannot precede acquired_at")
        if self.heartbeat_at < self.acquired_at:
            raise ValueError("heartbeat_at cannot precede acquired_at")

    def active(self, now: Optional[datetime] = None) -> bool:
        self.validate()
        current = now or datetime.now(timezone.utc)
        return current < self.expires_at


class LeaseRegistry:
    """In-memory reference implementation for lease ownership."""

    def __init__(self) -> None:
        self._leases = {}

    def acquire(self, task_id: str, owner_id: str, ttl_seconds: float, *, now: Optional[datetime] = None) -> ExecutionLease:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        current = now or datetime.now(timezone.utc)
        existing = self._leases.get(task_id)
        if existing is not None and existing.active(current) and existing.owner_id != owner_id:
            raise RuntimeError("task lease is held by another owner")

        lease = ExecutionLease(
            task_id=task_id,
            owner_id=owner_id,
            acquired_at=current,
            expires_at=current + timedelta(seconds=ttl_seconds),
            heartbeat_at=current,
        )
        lease.validate()
        self._leases[task_id] = lease
        return lease

    def heartbeat(self, task_id: str, owner_id: str, ttl_seconds: float, *, now: Optional[datetime] = None) -> ExecutionLease:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        current = now or datetime.now(timezone.utc)
        lease = self._leases.get(task_id)
        if lease is None:
            raise RuntimeError("no lease exists")
        if lease.owner_id != owner_id:
            raise RuntimeError("lease owner mismatch")
        if not lease.active(current):
            raise RuntimeError("lease has expired")

        renewed = replace(lease, heartbeat_at=current, expires_at=current + timedelta(seconds=ttl_seconds))
        renewed.validate()
        self._leases[task_id] = renewed
        return renewed

    def release(self, task_id: str, owner_id: str) -> None:
        lease = self._leases.get(task_id)
        if lease is None:
            return
        if lease.owner_id != owner_id:
            raise RuntimeError("lease owner mismatch")
        del self._leases[task_id]

    def get(self, task_id: str) -> Optional[ExecutionLease]:
        return self._leases.get(task_id)
