from core.idempotency import ExecutionReceipt, IdempotencyRegistry


def test_same_execution_key_returns_original_receipt():
    registry = IdempotencyRegistry()
    first = ExecutionReceipt("op-1", "task-1", True, "done")
    second = ExecutionReceipt("op-1", "task-1", True, "different")

    assert registry.record(first) == first
    assert registry.record(second) == first
    assert registry.completed("op-1")


def test_execution_key_cannot_switch_tasks():
    registry = IdempotencyRegistry()
    registry.record(ExecutionReceipt("op-1", "task-1", True))

    try:
        registry.record(ExecutionReceipt("op-1", "task-2", True))
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "another task" in str(exc)
