from core.durable_recovery_dispatch import SQLiteRecoveryDispatchStore
from core.models import Task
from core.policy_dispatch_claim import PolicyDispatchClaimAdapter
from core.execution_spine import ExecutionSpine


def decision(task_id="task-1", action="continue", allowed=True):
    return type(
        "Boundary",
        (),
        {
            "task_id": task_id,
            "action": action,
            "handoff_allowed": allowed,
            "reason": "test policy decision",
        },
    )()


def test_spine_connects_policy_claim_execution_and_provider(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "spine.sqlite"))
    spine = ExecutionSpine(PolicyDispatchClaimAdapter(store))
    task = Task(task_id="task-1", prompt="test")

    prepared = spine.prepare(task, decision(), "expected_progression", intent_id="intent-1")
    assert prepared.claim.claimed is True

    started = spine.start_execution(prepared)
    assert started.execution_start is not None
    assert started.execution_start.started is True

    accepted = spine.record_provider_acceptance(started, provider="echo", accepted=True)
    assert accepted.provider_acceptance is not None
    assert accepted.provider_acceptance.accepted is True
    assert accepted.provider_acceptance.provider == "echo"
    store.close()


def test_spine_blocks_execution_without_durable_claim(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "spine.sqlite"))
    spine = ExecutionSpine(PolicyDispatchClaimAdapter(store))
    task = Task(task_id="task-1", prompt="test")

    prepared = spine.prepare(task, decision(action="human_review", allowed=False), "identity_divergence", intent_id="intent-1")

    assert prepared.claim.claimed is False
    try:
        spine.start_execution(prepared)
    except RuntimeError as exc:
        assert "durable dispatch claim" in str(exc)
    else:
        raise AssertionError("execution should have been blocked")
    store.close()


def test_spine_preserves_explicit_intent_identity(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "spine.sqlite"))
    spine = ExecutionSpine(PolicyDispatchClaimAdapter(store))
    task = Task(task_id="task-1", prompt="test")

    prepared = spine.prepare(task, decision(), "expected_progression", intent_id="intent-xyz")
    started = spine.start_execution(prepared)

    assert started.intent_id == "intent-xyz"
    assert started.execution_start.intent_id == "intent-xyz"
    store.close()
