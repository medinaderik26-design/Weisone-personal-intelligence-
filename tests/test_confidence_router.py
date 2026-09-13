import unittest

from core.confidence_router import ConfidenceAwareRouter
from core.models import Task
from core.performance_confidence import ConfidencePolicy, PerformanceConfidence
from core.providers import SimulatedCloudProvider
from core.resource_manager import ResourceManager
from core.task_performance import TaskPerformanceRegistry


class TestConfidenceRouter(unittest.TestCase):
    def _router(self):
        local = SimulatedCloudProvider(name="local", model="local-model")
        cloud = SimulatedCloudProvider(name="cloud", model="cloud-model")
        resources = ResourceManager()
        resources.register_provider("local", model="local-model", requests_limit=10)
        resources.register_provider("cloud", model="cloud-model", requests_limit=10)
        history = TaskPerformanceRegistry()
        return local, cloud, resources, history

    def test_sparse_quality_does_not_control_routing(self):
        local, cloud, resources, history = self._router()
        history.record("cloud", "coding", success=True, quality=1.0)

        router = ConfidenceAwareRouter(
            [local, cloud],
            resources,
            history,
            PerformanceConfidence(ConfidencePolicy(min_samples=3, min_quality_samples=3)),
        )
        task = Task(task_id="t1", prompt="write code", metadata={"task_type": "coding"})

        # Sparse cloud evidence is not allowed to create a quality preference.
        self.assertEqual(router.select(task).name, "local")

    def test_sufficient_quality_evidence_can_control_routing(self):
        local, cloud, resources, history = self._router()
        for _ in range(3):
            history.record("cloud", "coding", success=True, quality=0.95)
        for _ in range(3):
            history.record("local", "coding", success=True, quality=0.70)

        router = ConfidenceAwareRouter(
            [local, cloud],
            resources,
            history,
            PerformanceConfidence(ConfidencePolicy(min_samples=3, min_quality_samples=3)),
        )
        task = Task(task_id="t2", prompt="write code", metadata={"task_type": "coding"})

        self.assertEqual(router.select(task).name, "cloud")


if __name__ == "__main__":
    unittest.main()
