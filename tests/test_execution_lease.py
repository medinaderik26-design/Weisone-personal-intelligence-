from datetime import datetime, timedelta, timezone

import pytest

from core.execution_lease import ExecutionLease, LeaseRegistry


def test_acquire_and_heartbeat_renew_lease():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    registry = LeaseRegistry()
    lease = registry.acquire("task-1", "worker-a", 30, now=now)

    assert lease.active(now)
    renewed = registry.heartbeat("task-1", "worker-a", 60, now=now + timedelta(seconds=10))
    assert renewed.heartbeat_at == now + timedelta(seconds=10)
    assert renewed.expires_at == now + timedelta(seconds=70)


def test_second_owner_cannot_take_active_lease():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    registry = LeaseRegistry()
    registry.acquire("task-1", "worker-a", 30, now=now)

    with pytest.raises(RuntimeError, match="held by another owner"):
        registry.acquire("task-1", "worker-b", 30, now=now + timedelta(seconds=5))


def test_expired_lease_can_be_reacquired():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    registry = LeaseRegistry()
    registry.acquire("task-1", "worker-a", 30, now=now)

    replacement = registry.acquire("task-1", "worker-b", 30, now=now + timedelta(seconds=31))
    assert replacement.owner_id == "worker-b"


def test_heartbeat_requires_owner_and_active_lease():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    registry = LeaseRegistry()
    registry.acquire("task-1", "worker-a", 30, now=now)

    with pytest.raises(RuntimeError, match="owner mismatch"):
        registry.heartbeat("task-1", "worker-b", 30, now=now + timedelta(seconds=1))

    with pytest.raises(RuntimeError, match="expired"):
        registry.heartbeat("task-1", "worker-a", 30, now=now + timedelta(seconds=31))


def test_invalid_lease_rejected():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    lease = ExecutionLease("task-1", "worker-a", now, now - timedelta(seconds=1), now)
    with pytest.raises(ValueError):
        lease.validate()
