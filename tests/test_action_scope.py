import pytest

from core.action_scope import ActionScope, ActionScopeGuard


def scope():
    return ActionScope(
        task_id="t1",
        operation="send_email",
        target="alice@example.com",
        purpose="respond to user-requested message",
        allowed_effects=("send",),
        confirmation_required=True,
        scope_id="scope-1",
    )


def test_matching_action_is_allowed():
    result = ActionScopeGuard().check(
        scope(), operation="send_email", target="alice@example.com", effect="send"
    )
    assert result.allowed is True


def test_different_target_is_denied():
    result = ActionScopeGuard().check(
        scope(), operation="send_email", target="bob@example.com", effect="send"
    )
    assert result.allowed is False


def test_extra_effect_is_denied():
    result = ActionScopeGuard().check(
        scope(), operation="send_email", target="alice@example.com", effect="delete"
    )
    assert result.allowed is False


def test_different_operation_is_denied():
    result = ActionScopeGuard().check(
        scope(), operation="create_calendar_event", target="alice@example.com", effect="send"
    )
    assert result.allowed is False


def test_invalid_scope_rejected():
    with pytest.raises(ValueError):
        ActionScope(task_id="", operation="send_email", target="x", purpose="y").validate()
