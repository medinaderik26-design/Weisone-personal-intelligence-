from datetime import datetime, timezone

import pytest

from core.action_ledger import ActionLedgerEntry
from core.ledger_recovery import LedgerRecoveryDecision
from core.persistent_work_state import WorkState
from core.reconciliation_record import ReconciliationRecord
from core.recovery_snapshot import RecoverySnapshotBuilder


def test_snapshot_binds_all_recovery_context():
    state = WorkState("task-1", "running")
    ledger = ActionLedgerEntry(
        task_id="task-1",
        intent_id="intent-1",
        operation="send_email",
        target="synthetic@example.test",
        stage="provider_accepted",
        statement="provider accepted",
        timestamp=datetime.now(timezone.utc),
    )
    reconciliation = ReconciliationRecord(
        task_id="task-1",
        intent_id="intent-1",
        prior_status="running",
        ledger_stage="provider_accepted",
        recovery_action="verify_external_effect",
        reason="external outcome unknown",
        recorded_at=datetime.now(timezone.utc),
    )
    decision = LedgerRecoveryDecision(
        "task-1", "verify_external_effect", "external outcome unknown", "provider_accepted", "intent-1"
    )

    snapshot = RecoverySnapshotBuilder().build(
        state, decision, ledger_entry=ledger, reconciliation=reconciliation
    )
    assert snapshot.task_id == "task-1"
    assert snapshot.latest_ledger.intent_id == "intent-1"
    assert snapshot.latest_reconciliation.recovery_action == "verify_external_effect"


def test_snapshot_rejects_mismatched_ledger_task():
    state = WorkState("task-1", "running")
    ledger = ActionLedgerEntry(
        task_id="task-2",
        intent_id="intent-2",
        operation="op",
        target="target",
        stage="executing",
        statement="executing",
        timestamp=datetime.now(timezone.utc),
    )
    decision = LedgerRecoveryDecision("task-1", "human_review", "mismatch")

    with pytest.raises(ValueError):
        RecoverySnapshotBuilder().build(state, decision, ledger_entry=ledger)
