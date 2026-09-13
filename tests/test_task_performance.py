import unittest

from core.task_performance import TaskPerformanceRegistry


class TestTaskPerformance(unittest.TestCase):
    def test_history_is_specific_to_provider_and_task(self):
        registry = TaskPerformanceRegistry()
        registry.record("local", "coding", success=True, quality=0.9, latency_ms=20)
        registry.record("local", "research", success=False, quality=0.2, latency_ms=80)
        registry.record("cloud", "coding", success=True, quality=0.8, latency_ms=10)

        coding_local = registry.get("local", "coding")
        research_local = registry.get("local", "research")
        coding_cloud = registry.get("cloud", "coding")

        self.assertEqual(coding_local.sample_count, 1)
        self.assertAlmostEqual(coding_local.quality_average, 0.9)
        self.assertAlmostEqual(research_local.quality_average, 0.2)
        self.assertAlmostEqual(coding_cloud.latency_average_ms, 10.0)

    def test_unknown_pair_has_no_quality_evidence(self):
        performance = TaskPerformanceRegistry().get("new", "research")
        self.assertEqual(performance.sample_count, 0)
        self.assertIsNone(performance.quality_average)
        self.assertIsNone(performance.latency_average_ms)


if __name__ == "__main__":
    unittest.main()
