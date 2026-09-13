from types import SimpleNamespace

from core.durable_policy_boundary import PolicyExecutionBoundary


def decision(action):
    return SimpleNamespace(task_id="task-1", action=action)


def test_continue_crosses_boundary():
    result = PolicyExecutionBoundary().evaluate(decision("continue"))
    assert result.handoff_allowed is True
    assert result.action == "continue"


def test_reinspect_does_not_cross_boundary():
    result = PolicyExecutionBoundary().evaluate(decision("reinspect"))
    assert result.handoff_allowed is False


def test_human_review_does_not_cross_boundary():
    result = PolicyExecutionBoundary().evaluate(decision("human_review"))
    assert result.handoff_allowed is False


def test_unknown_action_is_fail_closed():
    result = PolicyExecutionBoundary().evaluate(decision("execute"))
    assert result.handoff_allowed is False


def test_missing_identity_is_rejected():
    try:
        PolicyExecutionBoundary().evaluate(SimpleNamespace(task_id="", action="continue"))
    except ValueError as exc:
        assert "task_id" in str(exc)
    else:
        raise AssertionError("missing task_id should be rejected")
