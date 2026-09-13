import unittest

from core.provider_health import ProviderHealthRegistry


class TestProviderHealth(unittest.TestCase):
    def test_records_success_failure_quality_and_latency(self):
        registry = ProviderHealthRegistry()
        registry.record("local", success=True, quality=0.9, latency_ms=20)
        registry.record("local", success=False, quality=0.3, latency_ms=40)

        health = registry.get("local")
        self.assertEqual(health.successes, 1)
        self.assertEqual(health.failures, 1)
        self.assertEqual(health.success_rate, 0.5)
        self.assertAlmostEqual(health.quality_average, 0.6)
        self.assertAlmostEqual(health.latency_average_ms, 30.0)

    def test_unknown_provider_starts_empty(self):
        health = ProviderHealthRegistry().get("new-provider")
        self.assertEqual(health.successes, 0)
        self.assertEqual(health.failures, 0)
        self.assertIsNone(health.quality_average)
        self.assertIsNone(health.latency_average_ms)


if __name__ == "__main__":
    unittest.main()
