from core.scheduler_receipt import SchedulerReceipt, SQLiteSchedulerReceiptStore


def test_receipt_survives_restart(tmp_path):
    path = tmp_path / "receipt.db"
    store = SQLiteSchedulerReceiptStore(str(path))
    store.record(SchedulerReceipt("task-1", "intent-1", "dispatch-1", "handed_off", "t1"))
    store.close()

    reopened = SQLiteSchedulerReceiptStore(str(path))
    receipt = reopened.get("dispatch-1")
    assert receipt is not None
    assert receipt.state == "handed_off"
    assert receipt.intent_id == "intent-1"
    reopened.close()


def test_acceptance_is_forward_only_and_idempotent(tmp_path):
    store = SQLiteSchedulerReceiptStore(str(tmp_path / "receipt.db"))
    store.record(SchedulerReceipt("task-1", "intent-1", "dispatch-1", "handed_off", "t1"))
    store.record(SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "t2"))
    store.record(SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "t3"))
    assert store.get("dispatch-1").state == "accepted"
    store.close()


def test_identity_cannot_change(tmp_path):
    store = SQLiteSchedulerReceiptStore(str(tmp_path / "receipt.db"))
    store.record(SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "t1"))
    try:
        store.record(SchedulerReceipt("task-2", "intent-1", "dispatch-1", "accepted", "t2"))
    except ValueError as exc:
        assert str(exc) == "dispatch key identity changed"
    else:
        raise AssertionError("expected ValueError")
    store.close()
