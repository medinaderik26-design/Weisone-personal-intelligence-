import unittest

from core.execution_telemetry import ExecutionTelemetry


class TestExecutionTelemetry(unittest.TestCase):
    def test_serializes_normalized_execution(self):
        telemetry = ExecutionTelemetry(
            task_id="t-001",
            task_type="coding",
            provider="local",
            model="test-model",
            success=True,
            latency_ms=12.5,
            input_tokens=100,
            output_tokens=40,
            estimated_cost=0.0,
            quality=0.95,
            quality_source="human",
        )
        telemetry.validate()
        data = telemetry.to_dict()
        self.assertEqual(data["provider"], "local")
        self.assertEqual(data["input_tokens"], 100)
        self.assertEqual(data["quality_source"], "human")

    def test_unknown_quality_is_allowed(self):
        telemetry = ExecutionTelemetry(
            task_id="t-002",
            task_type="research",
            provider="cloud",
            model="model-a",
            success=True,
        )
        telemetry.validate()
        self.assertIsNone(telemetry.quality)

    def test_quality_requires_provenance(self):
        telemetry = ExecutionTelemetry(
            task_id="t-003",
            task_type="general",
            provider="cloud",
            model="model-a",
            success=True,
            quality=0.8,
        )
        with self.assertRaises(ValueError):
            telemetry.validate()

    def test_negative_resource_values_are_rejected(self):
        telemetry = ExecutionTelemetry(
            task_id="t-004",
            task_type="general",
            provider="local",
            model="model-a",
            success=True,
            input_tokens=-1,
        )
        with self.assertRaises(ValueError):
            telemetry.validate()


if __name__ == "__main__":
    unittest.main()
