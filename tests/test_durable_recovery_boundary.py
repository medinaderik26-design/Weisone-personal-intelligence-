from core.durable_recovery_boundary import RecoveryBoundaryRecord, SQLiteRecoveryBoundaryLog


def test_boundary_record_survives_reopen(tmp_path):
    path = tmp_path / "boundary.db"
    log = SQLiteRecoveryBoundaryLog(str(path))
    record = RecoveryBoundaryRecord.create(
        "task-1", "expected_progression", "continue", "snapshots show normal progression"
    )
    assert log.record(record) == 1
    log.close()

    reopened = SQLiteRecoveryBoundaryLog(str(path))
    records = reopened.for_task("task-1")
    reopened.close()

    assert len(records) == 1
    assert records[0].boundary == "execution_boundary"
    assert records[0].action == "continue"


def test_boundary_identity_is_validated():
    record = RecoveryBoundaryRecord.create("task-1", "x", "y", "z")
    record.validate()

    bad = RecoveryBoundaryRecord("task-1", "x", "y", "z", "wrong", record.recorded_at)
    try:
        bad.validate()
    except ValueError as exc:
        assert str(exc) == "invalid recovery boundary"
    else:
        raise AssertionError("expected invalid boundary")
