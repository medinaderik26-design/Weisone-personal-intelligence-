import unittest

from core.execution_feedback import ExecutionFeedbackLoop
from core.execution_telemetry import ExecutionTelemetry
from core.task_performance import TaskPerformanceRegistry
from core.telemetry_adapter import TelemetryAdapter


class TestTelemetryAdapter(unittest.TestCase):
    def test_telemetry_reaches_feedback_history(self):
        registry = TaskPerformanceRegistry()
        adapter = TelemetryAdapter(ExecutionFeedbackLoop(registry))

        adapter.record(
            ExecutionTelemetry(
                task_id="task-001",
                task_type="research",
                provider="local",
                model="local-test",
                success=True,
                latency_ms=18.0,
                quality=0.9,
                quality_source="benchmark",
            )
        )

        evidence = registry.get("local", "research")
        self.assertEqual(evidence.sample_count, 1)
        self.assertEqual(evidence.successes, 1)
        self.assertAlmostEqual(evidence.quality_average, 0.9)
        self.assertAlmostEqual(evidence.latency_average_ms, 18.0)

    def test_unknown_quality_stays_unknown(self):
        registry = TaskPerformanceRegistry()
        adapter = TelemetryAdapter(ExecutionFeedbackLoop(registry))

        adapter.record(
            ExecutionTelemetry(
                task_id="task-002",
                task_type="general",
                provider="cloud",
                model="cloud-test",
                success=True,
            )
        )

        evidence = registry.get("cloud", "general")
        self.assertIsNone(evidence.quality_average)


if __name__ == "__main__":
    unittest.main()
