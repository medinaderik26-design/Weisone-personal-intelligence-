from datetime import datetime, timedelta, timezone

from core.execution_lease import ExecutionLease, LeaseRegistry
from core.persistent_work_state import WorkState
from core.recovery_coordinator import RecoveryAction, RecoveryCoordinator
from core.recovery_engine import RecoveryEngine


def test_live_lease_prevents_recovery_reassignment():
    now = datetime(2026, 9, 13, tzinfo=timezone.utc)
    leases = LeaseRegistry()
    leases.acquire("task-1", "worker-a", 60, now=now)
    engine = RecoveryEngine(RecoveryCoordinator(), leases)

    inspection = engine.inspect(WorkState(task_id="task-1", status="running"), now=now)

    assert inspection.lease_active is True
    assert inspection.decision.action == RecoveryAction.DEFER


def test_expired_lease_routes_running_work_to_review():
    now = datetime(2026, 9, 13, tzinfo=timezone.utc)
    lease = ExecutionLease(
        task_id="task-2",
        owner_id="worker-a",
        acquired_at=now - timedelta(seconds=120),
        expires_at=now - timedelta(seconds=60),
        heartbeat_at=now - timedelta(seconds=120),
    )
    leases = LeaseRegistry()
    leases._leases["task-2"] = lease
    engine = RecoveryEngine(RecoveryCoordinator(), leases)

    inspection = engine.inspect(WorkState(task_id="task-2", status="running"), now=now)

    assert inspection.lease_active is False
    assert inspection.decision.action == RecoveryAction.HUMAN_REVIEW


def test_queued_work_can_resume_without_lease():
    leases = LeaseRegistry()
    engine = RecoveryEngine(RecoveryCoordinator(), leases)

    inspection = engine.inspect(WorkState(task_id="task-3", status="queued"))

    assert inspection.decision.action == RecoveryAction.RESUME
