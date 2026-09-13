from core.action_plan import ActionPlan, ActionPlanGuard, PlannedEffect
from core.action_scope import ActionScope
from core.execution_intent import ExecutionIntentRegistry, issue_from_plan
from core.idempotency import IdempotencyRegistry
from core.intent_idempotency import IntentIdempotencyBridge


def make_intent():
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
    return issue_from_plan(plan, confirmation, ExecutionIntentRegistry())


def test_new_intent_is_executable_with_its_own_key():
    intent = make_intent()
    result = IntentIdempotencyBridge(IdempotencyRegistry()).check(intent)
    assert result.executable is True
    assert result.execution_key == intent.intent_id


def test_successful_intent_cannot_execute_again():
    registry = IdempotencyRegistry()
    bridge = IntentIdempotencyBridge(registry)
    intent = make_intent()
    receipt = bridge.record(intent, success=True, response="sent")
    result = bridge.check(intent)
    assert receipt.execution_key == intent.intent_id
    assert result.executable is False
    assert result.reason == "logical action already completed"


def test_failed_attempt_reuses_same_execution_identity():
    registry = IdempotencyRegistry()
    bridge = IntentIdempotencyBridge(registry)
    intent = make_intent()
    bridge.record(intent, success=False, response="temporary failure")
    result = bridge.check(intent)
    assert result.executable is True
    assert result.execution_key == intent.intent_id
    assert result.receipt is not None


def test_receipt_task_mismatch_is_rejected():
    from core.idempotency import ExecutionReceipt
    registry = IdempotencyRegistry()
    intent = make_intent()
    registry.record(ExecutionReceipt(intent.intent_id, "different-task", True, "bad"))
    try:
        IntentIdempotencyBridge(registry).check(intent)
        assert False
    except ValueError:
        pass
