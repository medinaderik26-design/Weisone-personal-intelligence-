import unittest

from core.resource_outcome import ResourceOutcome, ResourceOutcomeRegistry


class TestResourceOutcome(unittest.TestCase):
    def test_records_and_aggregates_known_cost_and_tokens(self):
        registry = ResourceOutcomeRegistry()
        registry.record(ResourceOutcome("cloud-a", "t1", 100, 50, 200, 0.01))
        registry.record(ResourceOutcome("cloud-a", "t2", 80, 20, 150, 0.02))
        registry.record(ResourceOutcome("local", "t3", 40, 10, 80, 0.0))

        self.assertEqual(registry.total_tokens("cloud-a"), 250)
        self.assertAlmostEqual(registry.total_cost("cloud-a"), 0.03)
        self.assertEqual(len(registry.for_provider("local")), 1)

    def test_unknown_measurements_remain_unknown(self):
        registry = ResourceOutcomeRegistry()
        registry.record(ResourceOutcome("local", "t1"))
        self.assertIsNone(registry.total_tokens())
        self.assertIsNone(registry.total_cost())

    def test_invalid_measurements_are_rejected(self):
        registry = ResourceOutcomeRegistry()
        with self.assertRaises(ValueError):
            registry.record(ResourceOutcome("cloud", "t1", input_tokens=-2))

        with self.assertRaises(ValueError):
            registry.record(ResourceOutcome("cloud", "t2", cost=-0.1))


if __name__ == "__main__":
    unittest.main()
