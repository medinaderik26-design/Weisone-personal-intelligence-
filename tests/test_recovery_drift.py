from datetime import datetime, timezone

import pytest

from core.action_ledger import ActionLedgerEntry
from core.ledger_recovery import LedgerRecoveryDecision
from core.persistent_work_state import WorkState
from core.recovery_drift import RecoveryDriftDetector
from core.recovery_snapshot import RecoverySnapshotBuilder


def snapshot(status="running", stage="provider_accepted", action="verify_external_effect", attempts=1):
    state = WorkState("task-1", status, attempt_count=attempts, provider="local")
    entry = ActionLedgerEntry(
        task_id="task-1", intent_id="intent-1", operation="send_email",
        target="synthetic@example.test", stage=stage, statement=stage,
        timestamp=datetime.now(timezone.utc),
    )
    decision = LedgerRecoveryDecision("task-1", action, "external outcome unknown", stage, "intent-1")
    return RecoverySnapshotBuilder().build(state, decision, ledger_entry=entry)


def test_identical_snapshots_have_no_drift():
    detector = RecoveryDriftDetector()
    result = detector.compare(snapshot(), snapshot())
    assert result.changed is False
    assert result.changes == ()


def test_status_and_attempt_drift_are_detected():
    detector = RecoveryDriftDetector()
    result = detector.compare(snapshot(), snapshot(status="failed", attempts=2))
    assert result.changed is True
    assert "work_status" in result.changes
    assert "attempt_count" in result.changes


def test_ledger_stage_drift_is_detected():
    result = RecoveryDriftDetector().compare(
        snapshot(stage="provider_accepted"),
        snapshot(stage="externally_confirmed", action="complete"),
    )
    assert "ledger_stage" in result.changes
    assert "recovery_action" in result.changes


def test_different_tasks_cannot_be_compared():
    first = snapshot()
    second = RecoverySnapshotBuilder().build(
        WorkState("task-2", "running"),
        LedgerRecoveryDecision("task-2", "human_review", "different task"),
    )
    with pytest.raises(ValueError):
        RecoveryDriftDetector().compare(first, second)
