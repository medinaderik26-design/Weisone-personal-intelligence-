from datetime import datetime, timezone

from core.action_ledger import ActionLedgerEntry
from core.durable_recovery_snapshot import SQLiteRecoverySnapshotStore
from core.ledger_recovery import LedgerRecoveryDecision
from core.persistent_work_state import WorkState
from core.recovery_snapshot import RecoverySnapshotBuilder


def snapshot(stage="provider_accepted"):
    state = WorkState("task-1", "running")
    ledger = ActionLedgerEntry(
        task_id="task-1",
        intent_id="intent-1",
        operation="send_email",
        target="synthetic@example.test",
        stage=stage,
        statement=stage,
        timestamp=datetime.now(timezone.utc),
    )
    decision = LedgerRecoveryDecision(
        "task-1", "verify_external_effect", "external outcome unknown", stage, "intent-1"
    )
    return RecoverySnapshotBuilder().build(state, decision, ledger_entry=ledger)


def test_snapshots_are_versioned(tmp_path):
    store = SQLiteRecoverySnapshotStore(str(tmp_path / "snapshots.db"))
    assert store.save(snapshot()) == 1
    assert store.save(snapshot("executing")) == 2
    assert store.versions("task-1") == (1, 2)
    store.close()


def test_snapshot_versions_survive_reopen(tmp_path):
    path = str(tmp_path / "snapshots.db")
    first = SQLiteRecoverySnapshotStore(path)
    first.save(snapshot())
    first.close()

    second = SQLiteRecoverySnapshotStore(path)
    assert second.versions("task-1") == (1,)
    assert second.latest_json("task-1") is not None
    second.close()
