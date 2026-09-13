from types import SimpleNamespace

import pytest

from core.policy_dispatch_bridge import PolicyDispatchBridge


def boundary(task_id="task-1", action="continue", allowed=True):
    return SimpleNamespace(
        task_id=task_id,
        action=action,
        handoff_allowed=allowed,
        reason="test reason",
    )


def test_continue_builds_eligible_request_with_deterministic_key():
    bridge = PolicyDispatchBridge()

    first = bridge.build(boundary(), "expected_progression")
    second = bridge.build(boundary(), "expected_progression")

    assert first.eligible is True
    assert first.dispatch_key
    assert first.dispatch_key == second.dispatch_key
    assert first.reason == "policy boundary permits scheduler dispatch claim"


def test_reinspect_is_blocked():
    request = PolicyDispatchBridge().build(
        boundary(action="reinspect", allowed=False),
        "recoverable_divergence",
    )

    assert request.eligible is False
    assert request.dispatch_key is None


def test_human_review_is_blocked():
    request = PolicyDispatchBridge().build(
        boundary(action="human_review", allowed=False),
        "identity_divergence",
    )

    assert request.eligible is False
    assert request.dispatch_key is None


def test_unknown_action_fails_closed_even_if_flagged_allowed():
    request = PolicyDispatchBridge().build(
        boundary(action="unexpected", allowed=True),
        "unexpected_divergence",
    )

    assert request.eligible is False
    assert request.dispatch_key is None


def test_different_inputs_produce_different_keys():
    bridge = PolicyDispatchBridge()

    first = bridge.build(boundary("task-1"), "expected_progression")
    different_task = bridge.build(boundary("task-2"), "expected_progression")

    assert first.dispatch_key != different_task.dispatch_key


def test_required_identity_is_validated():
    bridge = PolicyDispatchBridge()

    with pytest.raises(ValueError):
        bridge.build(boundary(task_id=""), "expected_progression")

    with pytest.raises(ValueError):
        bridge.build(boundary(), "")
