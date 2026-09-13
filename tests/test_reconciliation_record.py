from datetime import datetime, timezone

from core.ledger_recovery import LedgerRecoveryDecision
from core.persistent_work_state import WorkState
from core.reconciliation_record import ReconciliationLog, ReconciliationRecord


def test_reconciliation_captures_recovery_context():
    state = WorkState("task-1", "running")
    decision = LedgerRecoveryDecision(
        task_id="task-1",
        action="verify_external_effect",
        reason="external outcome is unknown",
        current_stage="provider_accepted",
        intent_id="intent-1",
    )

    record = ReconciliationRecord.from_decision(
        state,
        decision,
        now=datetime(2026, 9, 13, tzinfo=timezone.utc),
    )

    assert record.task_id == "task-1"
    assert record.intent_id == "intent-1"
    assert record.prior_status == "running"
    assert record.ledger_stage == "provider_accepted"
    assert record.recovery_action == "verify_external_effect"


def test_log_is_append_only_reference_history():
    log = ReconciliationLog()
    record = ReconciliationRecord(
        task_id="task-1",
        intent_id="intent-1",
        prior_status="running",
        ledger_stage="provider_accepted",
        recovery_action="verify_external_effect",
        reason="external outcome is unknown",
        recorded_at=datetime.now(timezone.utc),
    )
    log.append(record)
    assert log.for_task("task-1") == (record,)
