import pytest

from core.recovery_idempotency import RecoveryDispatchGuard, RecoveryDispatchKey


def test_same_recovery_decision_can_only_be_claimed_once():
    guard = RecoveryDispatchGuard()
    key = RecoveryDispatchKey("task-1", "recoverable_divergence", "reinspect")

    assert guard.claim(key, 1) is True
    assert guard.claim(key, 1) is False
    assert guard.boundary_record_id(key) == "1"


def test_different_actions_are_distinct_dispatches():
    guard = RecoveryDispatchGuard()
    first = RecoveryDispatchKey("task-1", "recoverable_divergence", "reinspect")
    second = RecoveryDispatchKey("task-1", "recoverable_divergence", "human_review")

    assert guard.claim(first, 1) is True
    assert guard.claim(second, 2) is True


def test_invalid_boundary_record_is_rejected():
    guard = RecoveryDispatchGuard()
    key = RecoveryDispatchKey("task-1", "x", "y")
    with pytest.raises(ValueError):
        guard.claim(key, 0)
