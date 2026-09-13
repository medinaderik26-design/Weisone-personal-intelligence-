from core.action_plan import ActionPlan, ActionPlanGuard, PlannedEffect
from core.action_scope import ActionScope
from core.execution_intent import ExecutionIntentRegistry, issue_from_plan


def make_confirmed_plan():
    scope = ActionScope(
        task_id="t1",
        operation="send_email",
        target="alice@example.com",
        purpose="send requested response",
        allowed_effects=("send",),
        confirmation_required=True,
        scope_id="scope-1",
    )
    plan = ActionPlan(
        scope,
        (PlannedEffect("send", "alice@example.com", "send approved response"),),
    )
    confirmation = ActionPlanGuard().confirm(plan, confirmed=True)
    return plan, confirmation


def test_intent_binds_to_confirmed_plan():
    plan, confirmation = make_confirmed_plan()
    registry = ExecutionIntentRegistry()
    intent = issue_from_plan(plan, confirmation, registry)
    assert intent.task_id == "t1"
    assert intent.scope_id == "scope-1"
    assert intent.confirmed_effects == ("send",)
    assert intent.consumed is False


def test_intent_is_one_shot():
    _, confirmation = make_confirmed_plan()
    registry = ExecutionIntentRegistry()
    intent = registry.issue(confirmation)
    consumed = registry.consume(intent.intent_id)
    assert consumed.consumed is True

    try:
        registry.consume(intent.intent_id)
        assert False
    except RuntimeError:
        pass


def test_unknown_intent_rejected():
    registry = ExecutionIntentRegistry()
    try:
        registry.consume("missing")
        assert False
    except KeyError:
        pass


def test_mismatched_confirmation_rejected():
    plan, confirmation = make_confirmed_plan()
    bad = type(confirmation)(
        task_id=confirmation.task_id,
        scope_id=confirmation.scope_id,
        confirmed_effects=("delete",),
    )
    try:
        issue_from_plan(plan, bad, ExecutionIntentRegistry())
        assert False
    except ValueError:
        pass
