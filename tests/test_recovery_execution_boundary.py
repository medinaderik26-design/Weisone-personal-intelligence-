from core.recovery_coordinator import RecoveryAction, RecoveryDecision
from core.recovery_execution_boundary import RecoveryExecutionBoundary
from core.recovery_policy import RecoveryPolicyDecision
from core.scheduler_recovery import SchedulerAction


def decision():
    return RecoveryDecision(
        task_id="task-1",
        action=RecoveryAction.RESUME,
        reason="queued work can resume",
        provider="local",
    )


def test_no_drift_reaches_scheduler_controller():
    result = RecoveryExecutionBoundary().apply(
        decision(),
        RecoveryPolicyDecision("no_drift", "continue", "no changes"),
    )
    assert result.scheduled.action == SchedulerAction.ENQUEUE


def test_recoverable_drift_is_deferred_for_reinspection():
    result = RecoveryExecutionBoundary().apply(
        decision(),
        RecoveryPolicyDecision("recoverable_divergence", "reinspect", "reinspect state"),
    )
    assert result.scheduled.action == SchedulerAction.DEFER
    assert result.scheduled.reason == "reinspect state"


def test_sensitive_drift_stops_automatic_execution():
    result = RecoveryExecutionBoundary().apply(
        decision(),
        RecoveryPolicyDecision("human_review_required", "human_review", "identity drift"),
    )
    assert result.scheduled.action == SchedulerAction.HUMAN_REVIEW
    assert result.scheduled.reason == "identity drift"
