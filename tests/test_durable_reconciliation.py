from datetime import datetime, timezone

from core.durable_reconciliation import SQLiteReconciliationLog
from core.reconciliation_record import ReconciliationRecord


def make_record():
    return ReconciliationRecord(
        task_id="task-1",
        intent_id="intent-1",
        prior_status="running",
        ledger_stage="provider_accepted",
        recovery_action="verify_external_effect",
        reason="external outcome is unknown",
        recorded_at=datetime.now(timezone.utc),
    )


def test_reconciliation_survives_reopen(tmp_path):
    path = str(tmp_path / "reconciliation.db")
    first = SQLiteReconciliationLog(path)
    record = make_record()
    first.append(record)
    first.close()

    second = SQLiteReconciliationLog(path)
    recovered = second.for_task("task-1")
    assert recovered == (record,)
    second.close()


def test_unknown_task_has_empty_history(tmp_path):
    log = SQLiteReconciliationLog(str(tmp_path / "reconciliation.db"))
    assert log.for_task("missing") == ()
    log.close()
