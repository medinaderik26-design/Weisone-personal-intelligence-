from core.durable_dispatch_ack import DispatchAcknowledgement, SQLiteDispatchAcknowledgementStore


def test_ack_state_survives_restart_and_cannot_regress(tmp_path):
    path = tmp_path / "ack.db"
    store = SQLiteDispatchAcknowledgementStore(str(path))
    store.record(DispatchAcknowledgement("task-1", "key-1", "claimed", "t1"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "handed_off", "t2"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "accepted", "t3"))
    store.close()

    reopened = SQLiteDispatchAcknowledgementStore(str(path))
    assert reopened.get("key-1").state == "accepted"
    reopened.close()


def test_backward_transition_is_rejected(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "accepted", "t1"))
    try:
        store.record(DispatchAcknowledgement("task-1", "key-1", "claimed", "t2"))
    except ValueError as exc:
        assert str(exc) == "acknowledgement state cannot move backward"
    else:
        raise AssertionError("expected ValueError")
    store.close()
