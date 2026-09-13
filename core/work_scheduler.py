"""PI-018 work queue and scheduler for resource-constrained intelligence execution."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .models import Task


@dataclass(order=True)
class QueuedTask:
    """A task waiting for an execution opportunity."""

    priority: int
    sequence: int
    task: Task = field(compare=False)
    attempts: int = field(default=0, compare=False)
    last_reason: Optional[str] = field(default=None, compare=False)


class WorkScheduler:
    """Preserve tasks when no suitable provider can execute them immediately.

    The scheduler is provider-agnostic. A caller supplies an executor that either
    executes a task or raises a retryable RuntimeError when capacity is unavailable.
    """

    def __init__(self) -> None:
        self._queue: List[QueuedTask] = []
        self._sequence = 0
        self._completed: Dict[str, Task] = {}
        self._failed: Dict[str, str] = {}

    def enqueue(self, task: Task, *, priority: int = 0, reason: Optional[str] = None) -> QueuedTask:
        if task.task_id in self._completed:
            raise ValueError(f"task {task.task_id} is already completed")
        if any(item.task.task_id == task.task_id for item in self._queue):
            raise ValueError(f"task {task.task_id} is already queued")

        item = QueuedTask(
            priority=-priority,
            sequence=self._sequence,
            task=task,
            last_reason=reason,
        )
        self._sequence += 1
        self._queue.append(item)
        self._queue.sort()
        return item

    def pending(self) -> List[QueuedTask]:
        return list(self._queue)

    def run_next(self, executor: Callable[[Task], object]) -> object:
        if not self._queue:
            return None

        item = self._queue.pop(0)
        item.attempts += 1

        try:
            result = executor(item.task)
        except RuntimeError as exc:
            item.last_reason = str(exc)
            self._queue.append(item)
            self._queue.sort()
            return None
        except Exception as exc:
            self._failed[item.task.task_id] = str(exc)
            raise

        self._completed[item.task.task_id] = item.task
        return result

    def pending_ids(self) -> List[str]:
        return [item.task.task_id for item in self._queue]

    def completed_ids(self) -> List[str]:
        return list(self._completed)

    def failed(self) -> Dict[str, str]:
        return dict(self._failed)
