from core.durable_dispatch_ack import DispatchAcknowledgement, SQLiteDispatchAcknowledgementStore
from core.recovery_dispatch_inspection import RecoveryDispatchInspector


def test_missing_ack_requires_resume_handoff(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    decision = RecoveryDispatchInspector(store).inspect("task-1", "key-1")
    assert decision.action == "resume_handoff"
    store.close()


def test_claimed_ack_requires_handoff_resume(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "claimed", "t1"))
    decision = RecoveryDispatchInspector(store).inspect("task-1", "key-1")
    assert decision.action == "resume_handoff"
    store.close()


def test_handed_off_ack_requires_acceptance_verification(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "handed_off", "t1"))
    decision = RecoveryDispatchInspector(store).inspect("task-1", "key-1")
    assert decision.action == "verify_acceptance"
    store.close()


def test_accepted_ack_allows_continuation_but_not_completion_claim(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "accepted", "t1"))
    decision = RecoveryDispatchInspector(store).inspect("task-1", "key-1")
    assert decision.action == "continue"
    assert "execution outcome remains a separate boundary" in decision.reason
    store.close()


def test_wrong_task_is_rejected(tmp_path):
    store = SQLiteDispatchAcknowledgementStore(str(tmp_path / "ack.db"))
    store.record(DispatchAcknowledgement("task-1", "key-1", "accepted", "t1"))
    try:
        RecoveryDispatchInspector(store).inspect("task-2", "key-1")
    except ValueError as exc:
        assert str(exc) == "dispatch key is bound to a different task"
    else:
        raise AssertionError("expected ValueError")
    store.close()
