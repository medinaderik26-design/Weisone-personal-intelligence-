from core.models import Task
from core.work_scheduler import WorkScheduler


def test_scheduler_preserves_task_when_capacity_is_unavailable():
    scheduler = WorkScheduler()
    task = Task(task_id="q1", prompt="important work")
    scheduler.enqueue(task, priority=5, reason="quota exhausted")

    calls = []

    def unavailable_executor(received):
        calls.append(received.task_id)
        raise RuntimeError("provider quota exhausted")

    assert scheduler.run_next(unavailable_executor) is None
    assert scheduler.pending_ids() == ["q1"]
    assert calls == ["q1"]


def test_scheduler_executes_high_priority_first():
    scheduler = WorkScheduler()
    low = Task(task_id="low", prompt="low")
    high = Task(task_id="high", prompt="high")
    scheduler.enqueue(low, priority=1)
    scheduler.enqueue(high, priority=10)

    seen = []
    assert scheduler.run_next(lambda task: seen.append(task.task_id) or "ok") == "ok"
    assert seen == ["high"]
    assert scheduler.pending_ids() == ["low"]


def test_scheduler_records_success_and_keeps_task_identity():
    scheduler = WorkScheduler()
    task = Task(task_id="q2", prompt="continue this")
    scheduler.enqueue(task)

    result = scheduler.run_next(lambda received: {"task_id": received.task_id})

    assert result == {"task_id": "q2"}
    assert scheduler.pending_ids() == []
    assert scheduler.completed_ids() == ["q2"]


def test_scheduler_does_not_duplicate_task():
    scheduler = WorkScheduler()
    task = Task(task_id="q3", prompt="one task")
    scheduler.enqueue(task)

    try:
        scheduler.enqueue(task)
        assert False, "expected duplicate queue rejection"
    except ValueError as exc:
        assert "already queued" in str(exc)
