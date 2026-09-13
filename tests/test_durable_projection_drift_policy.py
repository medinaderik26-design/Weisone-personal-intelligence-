from datetime import datetime, timezone

from core.durable_projection_drift_policy import (
    DurableProjectionPolicyDecision,
    SQLiteProjectionDriftPolicyLog,
)


def test_policy_decision_survives_restart(tmp_path):
    db = tmp_path / "projection-policy.sqlite"
    recorded_at = datetime(2026, 9, 13, tzinfo=timezone.utc)
    decision = DurableProjectionPolicyDecision.create(
        "task-1",
        "expected_progression",
        "continue",
        "lifecycle stage advanced",
        now=recorded_at,
    )

    store = SQLiteProjectionDriftPolicyLog(str(db))
    store.record(decision)
    store.close()

    reopened = SQLiteProjectionDriftPolicyLog(str(db))
    records = reopened.for_task("task-1")
    assert records == (decision,)
    reopened.close()


def test_policy_decisions_preserve_order_and_task_scope(tmp_path):
    store = SQLiteProjectionDriftPolicyLog(str(tmp_path / "projection-policy.sqlite"))
    first = DurableProjectionPolicyDecision.create(
        "task-1", "expected_progression", "continue", "stage advanced"
    )
    second = DurableProjectionPolicyDecision.create(
        "task-1", "unexpected_divergence", "reinspect", "unexpected state change"
    )
    other = DurableProjectionPolicyDecision.create(
        "task-2", "no_drift", "continue", "projection is unchanged"
    )

    store.record(first)
    store.record(second)
    store.record(other)

    assert store.for_task("task-1") == (first, second)
    assert store.for_task("task-2") == (other,)
    assert store.all() == (first, second, other)
    store.close()
