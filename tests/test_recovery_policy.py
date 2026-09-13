from core.recovery_drift import RecoveryDrift
from core.recovery_policy import RecoveryReconciliationPolicy


def test_no_drift_continues():
    result = RecoveryReconciliationPolicy().classify(RecoveryDrift(False))
    assert result.classification == "no_drift"
    assert result.action == "continue"


def test_narrative_only_drift_is_expected_progression():
    result = RecoveryReconciliationPolicy().classify(
        RecoveryDrift(True, ("ledger_stage", "recovery_action"))
    )
    assert result.classification == "expected_progression"
    assert result.action == "continue"


def test_work_state_drift_requires_reinspection():
    result = RecoveryReconciliationPolicy().classify(
        RecoveryDrift(True, ("work_status", "attempt_count"))
    )
    assert result.classification == "recoverable_divergence"
    assert result.action == "reinspect"


def test_mixed_sensitive_drift_requires_human_review():
    result = RecoveryReconciliationPolicy().classify(
        RecoveryDrift(True, ("provider", "intent_id"))
    )
    assert result.classification == "human_review_required"
    assert result.action == "human_review"
