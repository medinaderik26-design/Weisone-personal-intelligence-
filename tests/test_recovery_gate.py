from core.idempotency import ExecutionReceipt, IdempotencyRegistry
from core.persistent_work_state import WorkState
from core.recovery_coordinator import RecoveryCoordinator
from core.recovery_gate import RecoveryExecutionGate
from core.retry_policy import RetryPolicy


def make_gate():
    return RecoveryExecutionGate(
        RecoveryCoordinator(),
        IdempotencyRegistry(),
        RetryPolicy(max_attempts=3),
    )


def test_queued_work_can_resume():
    gate = make_gate()
    result = gate.evaluate(
        WorkState(task_id="t1", status="queued", attempt_count=0),
        execution_key="k1",
    )
    assert result.execution_allowed is True
    assert result.decision.action == "resume"


def test_completed_execution_key_blocks_duplicate():
    idempotency = IdempotencyRegistry()
    idempotency.record(ExecutionReceipt("k1", "t1", True, "ok"))
    gate = RecoveryExecutionGate(RecoveryCoordinator(), idempotency)

    result = gate.evaluate(
        WorkState(task_id="t1", status="queued"),
        execution_key="k1",
    )
    assert result.execution_allowed is False
    assert "successful receipt" in result.reason


def test_interrupted_running_work_requires_review():
    gate = make_gate()
    result = gate.evaluate(
        WorkState(task_id="t1", status="running", attempt_count=1),
        execution_key="k1",
        external_completion_unknown=True,
    )
    assert result.execution_allowed is False
    assert result.decision.action == "human_review"


def test_retry_is_allowed_only_with_retry_budget():
    gate = make_gate()
    result = gate.evaluate(
        WorkState(task_id="t1", status="failed", attempt_count=1),
        execution_key="k1",
        external_completion_unknown=False,
        retryable=True,
    )
    assert result.execution_allowed is True
    assert result.decision.action == "retry"

    exhausted = gate.evaluate(
        WorkState(task_id="t2", status="failed", attempt_count=3),
        execution_key="k2",
        external_completion_unknown=False,
        retryable=True,
    )
    assert exhausted.execution_allowed is False
