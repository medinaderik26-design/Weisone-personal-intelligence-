import pytest

from core.action_plan import ActionPlan, ActionPlanGuard, PlannedEffect
from core.action_scope import ActionScope


def make_plan():
    scope = ActionScope(
        task_id="t1",
        operation="send_email",
        target="alice@example.com",
        purpose="send requested response",
        allowed_effects=("send",),
        confirmation_required=True,
        scope_id="scope-1",
    )
    return ActionPlan(
        scope=scope,
        effects=(PlannedEffect("send", "alice@example.com", "send the approved response"),),
    )


def test_preview_contains_concrete_effect():
    assert make_plan().preview() == (
        "send → alice@example.com: send the approved response",
    )


def test_unconfirmed_plan_is_blocked():
    with pytest.raises(PermissionError):
        ActionPlanGuard().confirm(make_plan(), confirmed=False)


def test_confirmed_plan_returns_exact_scope_and_effects():
    result = ActionPlanGuard().confirm(make_plan(), confirmed=True)
    assert result.task_id == "t1"
    assert result.scope_id == "scope-1"
    assert result.confirmed_effects == ("send",)


def test_plan_cannot_expand_beyond_scope():
    plan = make_plan()
    expanded = ActionPlan(
        plan.scope,
        plan.effects + (PlannedEffect("delete", "alice@example.com", "delete data"),),
    )
    with pytest.raises(ValueError):
        expanded.validate()
