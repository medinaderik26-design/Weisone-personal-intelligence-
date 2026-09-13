"""PI-010 execution feedback: convert completed runs into measured observations."""

from dataclasses import dataclass
from typing import Optional

from .task_performance import TaskPerformanceRegistry


@dataclass(frozen=True)
class ExecutionFeedback:
    provider: str
    task_type: str
    success: bool
    quality: Optional[float] = None
    latency_ms: Optional[float] = None


class ExecutionFeedbackLoop:
    """Record explicit execution outcomes into task-specific performance history."""

    def __init__(self, performance: TaskPerformanceRegistry) -> None:
        self.performance = performance

    def observe(self, feedback: ExecutionFeedback):
        return self.performance.record(
            feedback.provider,
            feedback.task_type,
            success=feedback.success,
            quality=feedback.quality,
            latency_ms=feedback.latency_ms,
        )
