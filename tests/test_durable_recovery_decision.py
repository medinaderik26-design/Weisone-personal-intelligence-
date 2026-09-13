from core.durable_recovery_decision import DurableRecoveryDecision, SQLiteRecoveryDecisionLog


def test_decision_log_survives_reopen(tmp_path):
    path = tmp_path / "recovery.db"
    first = SQLiteRecoveryDecisionLog(str(path))
    decision = DurableRecoveryDecision.create(
        "task-1", "recoverable_divergence", "reinspect", "work state changed"
    )
    row_id = first.append(decision)
    first.close()

    second = SQLiteRecoveryDecisionLog(str(path))
    records = second.for_task("task-1")
    second.close()

    assert row_id == 1
    assert len(records) == 1
    assert records[0].classification == "recoverable_divergence"
    assert records[0].action == "reinspect"
    assert records[0].reason == "work state changed"


def test_decision_requires_reason():
    try:
        DurableRecoveryDecision.create("task-1", "x", "y", "")
    except ValueError as exc:
        assert str(exc) == "reason is required"
    else:
        raise AssertionError("expected ValueError")
