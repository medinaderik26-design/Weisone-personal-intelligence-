import unittest

from core.execution_evidence import ExecutionEvidence, ExecutionEvidenceRecorder
from core.execution_telemetry import ExecutionTelemetry
from core.resource_outcome import ResourceOutcome


class TestExecutionEvidence(unittest.TestCase):
    def make_evidence(self):
        telemetry = ExecutionTelemetry(
            task_id="task-1",
            task_type="research",
            provider="cloud-a",
            model="model-a",
            success=True,
            latency_ms=120,
            input_tokens=100,
            output_tokens=50,
            estimated_cost=0.02,
            quality=0.9,
            quality_source="human_review",
        )
        resource = ResourceOutcome(
            provider="cloud-a",
            task_id="task-1",
            input_tokens=100,
            output_tokens=50,
            latency_ms=120,
            cost=0.02,
        )
        return ExecutionEvidence(telemetry, resource)

    def test_valid_evidence_is_recorded(self):
        recorder = ExecutionEvidenceRecorder()
        evidence = self.make_evidence()
        self.assertIs(recorder.record(evidence), evidence)
        self.assertIs(recorder.latest(), evidence)
        self.assertEqual(len(recorder.for_task("task-1")), 1)

    def test_mismatched_task_ids_are_rejected(self):
        evidence = self.make_evidence()
        resource = ResourceOutcome("cloud-a", "task-2")
        evidence = ExecutionEvidence(evidence.telemetry, resource)
        with self.assertRaises(ValueError):
            evidence.validate()

    def test_mismatched_providers_are_rejected(self):
        evidence = self.make_evidence()
        resource = ResourceOutcome("local", "task-1")
        evidence = ExecutionEvidence(evidence.telemetry, resource)
        with self.assertRaises(ValueError):
            evidence.validate()


if __name__ == "__main__":
    unittest.main()
