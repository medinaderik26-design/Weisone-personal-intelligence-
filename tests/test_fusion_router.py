import unittest

from core.fusion_router import PerformanceResourceFusionRouter
from core.models import ResourceSnapshot, Result, Task
from core.providers import IntelligenceProvider
from core.resource_manager import ResourceManager
from core.task_performance import TaskPerformanceRegistry


class FakeProvider(IntelligenceProvider):
    def __init__(self, name, latency_ms=100, remaining_quota=10):
        self.name = name
        self.model = name + "-model"
        self._snapshot = ResourceSnapshot(
            provider=name,
            model=self.model,
            available=True,
            remaining_quota=remaining_quota,
            latency_ms=latency_ms,
            requests_used=0,
            requests_limit=10,
        )

    def resource_snapshot(self):
        return self._snapshot

    def generate(self, task):
        return Result(task.task_id, self.name, self.model, "ok")


class TestFusionRouter(unittest.TestCase):
    def setUp(self):
        self.resources = ResourceManager()
        self.performance = TaskPerformanceRegistry()
        self.providers = [FakeProvider("cloud-a", latency_ms=300), FakeProvider("cloud-b", latency_ms=100)]
        for provider in self.providers:
            self.resources.register_provider(provider.name, provider.model, 10)

    def test_quality_can_outweigh_latency(self):
        for _ in range(3):
            self.performance.record("cloud-a", "research", True, quality=0.95, latency_ms=300)
            self.performance.record("cloud-b", "research", True, quality=0.70, latency_ms=100)

        router = PerformanceResourceFusionRouter(self.providers, self.resources, self.performance)
        task = Task("t1", "research", metadata={"task_type": "research", "low_latency": True})
        self.assertEqual(router.select(task).name, "cloud-a")

    def test_unknown_quality_does_not_receive_quality_bonus(self):
        router = PerformanceResourceFusionRouter(self.providers, self.resources, self.performance)
        task = Task("t2", "general")
        self.assertEqual(router.select(task).name, "cloud-a")

    def test_high_privacy_forces_local_when_available(self):
        local = FakeProvider("local")
        self.resources.register_provider(local.name, local.model, 10)
        router = PerformanceResourceFusionRouter(self.providers + [local], self.resources, self.performance)
        task = Task("t3", "private", privacy="high")
        self.assertEqual(router.select(task).name, "local")


if __name__ == "__main__":
    unittest.main()
