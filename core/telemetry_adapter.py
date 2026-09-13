"""PI-012 adapter connecting execution results to standardized telemetry."""

from dataclasses import dataclass
from typing import Optional

from .execution_feedback import ExecutionFeedback, ExecutionFeedbackLoop
from .execution_telemetry import ExecutionTelemetry


@dataclass(frozen=True)
class TelemetryAdapter:
    """Translate measured execution facts into PI feedback without inventing data."""

    feedback_loop: ExecutionFeedbackLoop

    def record(self, telemetry: ExecutionTelemetry):
        telemetry.validate()
        feedback = ExecutionFeedback(
            provider=telemetry.provider,
            task_type=telemetry.task_type,
            success=telemetry.success,
            quality=telemetry.quality,
            latency_ms=telemetry.latency_ms,
        )
        return self.feedback_loop.observe(feedback)
