import unittest

from core.models import Task
from core.providers import IntelligenceProvider, ProviderResourceSnapshot
from core.resource_manager import ResourceManager
from core.resource_policy import ResourceAwareDecisionPolicy


class FakeProvider(IntelligenceProvider):
    def __init__(self, name, available=True, used=0, limit=10, latency_ms=None):
        self.name = name
        self.model = f"{name}-model"
        self._snapshot = ProviderResourceSnapshot(
            available=available,
            requests_used=used,
            requests_limit=limit,
            latency_ms=latency_ms,
        )

    def generate(self, task):
        raise NotImplementedError

    def resource_snapshot(self):
        return self._snapshot


class TestResourceAwareDecisionPolicy(unittest.TestCase):
    def setUp(self):
        self.resources = ResourceManager()
        self.providers = [
            FakeProvider("cloud-a", used=9, limit=10, latency_ms=300),
            FakeProvider("cloud-b", used=2, limit=10, latency_ms=100),
            FakeProvider("local", used=1, limit=10, latency_ms=500),
        ]
        for provider in self.providers:
            self.resources.register_provider(provider.name, provider.model, provider.resource_snapshot().requests_limit)

    def test_low_latency_prefers_lower_measured_latency(self):
        task = Task(task_id="t1", prompt="hello", metadata={"low_latency": True})
        ranked = ResourceAwareDecisionPolicy(self.resources).rank(task, self.providers)
        self.assertEqual(ranked[0].name, "cloud-b")

    def test_high_privacy_allows_only_local(self):
        task = Task(task_id="t2", prompt="private", privacy="high")
        ranked = ResourceAwareDecisionPolicy(self.resources).rank(task, self.providers)
        self.assertEqual([p.name for p in ranked], ["local"])

    def test_unavailable_provider_is_excluded(self):
        providers = [FakeProvider("cloud-a", available=False), FakeProvider("cloud-b")]
        for provider in providers:
            self.resources.register_provider(provider.name, provider.model, provider.resource_snapshot().requests_limit)
        task = Task(task_id="t3", prompt="hello")
        ranked = ResourceAwareDecisionPolicy(self.resources).rank(task, providers)
        self.assertEqual([p.name for p in ranked], ["cloud-b"])


if __name__ == "__main__":
    unittest.main()
