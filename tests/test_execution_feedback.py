import unittest

from core.execution_feedback import ExecutionFeedback, ExecutionFeedbackLoop
from core.task_performance import TaskPerformanceRegistry


class TestExecutionFeedback(unittest.TestCase):
    def test_observation_updates_task_specific_history(self):
        registry = TaskPerformanceRegistry()
        loop = ExecutionFeedbackLoop(registry)

        loop.observe(ExecutionFeedback("cloud", "coding", True, quality=0.9, latency_ms=40))
        loop.observe(ExecutionFeedback("cloud", "coding", False, quality=0.2, latency_ms=60))

        evidence = registry.get("cloud", "coding")
        self.assertEqual(evidence.successes, 1)
        self.assertEqual(evidence.failures, 1)
        self.assertAlmostEqual(evidence.quality_average, 0.55)
        self.assertAlmostEqual(evidence.latency_average_ms, 50.0)

    def test_missing_quality_is_preserved_as_unknown(self):
        registry = TaskPerformanceRegistry()
        loop = ExecutionFeedbackLoop(registry)

        loop.observe(ExecutionFeedback("local", "research", True, latency_ms=25))

        evidence = registry.get("local", "research")
        self.assertEqual(evidence.successes, 1)
        self.assertIsNone(evidence.quality_average)


if __name__ == "__main__":
    unittest.main()
