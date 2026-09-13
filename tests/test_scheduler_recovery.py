from core.recovery_coordinator import RecoveryAction, RecoveryDecision
from core.scheduler_recovery import SchedulerAction, SchedulerRecoveryController


def test_resume_becomes_enqueue():
    decision = RecoveryDecision("t1", RecoveryAction.RESUME, "incomplete work")
    result = SchedulerRecoveryController().apply(decision)
    assert result.action == SchedulerAction.ENQUEUE


def test_retry_preserves_provider_and_reason():
    decision = RecoveryDecision("t2", RecoveryAction.RETRY, "retry allowed", "local")
    result = SchedulerRecoveryController().apply(decision)
    assert result.action == SchedulerAction.RETRY
    assert result.provider == "local"
    assert result.reason == "retry allowed"


def test_human_review_is_never_converted_to_execution():
    decision = RecoveryDecision("t3", RecoveryAction.HUMAN_REVIEW, "external completion unknown")
    result = SchedulerRecoveryController().apply(decision)
    assert result.action == SchedulerAction.HUMAN_REVIEW
