import unittest

from core.models import Task
from core.providers import EchoProvider, SimulatedCloudProvider
from core.resource_manager import ResourceManager
from core.router import IntelligenceRouter


class TestPI004Routing(unittest.TestCase):
    def test_falls_back_when_first_provider_is_exhausted(self):
        manager = ResourceManager()
        local = EchoProvider()
        cloud = SimulatedCloudProvider(requests_limit=1)
        router = IntelligenceRouter([cloud, local], manager)

        first = router.select(Task(task_id="PI-004-A", prompt="first"))
        self.assertEqual(first.name, "cloud-sim")

        manager.record_request("cloud-sim")
        second = router.select(Task(task_id="PI-004-B", prompt="second"))
        self.assertEqual(second.name, "local")

    def test_unavailable_provider_is_skipped(self):
        manager = ResourceManager()
        cloud = SimulatedCloudProvider(available=False)
        local = EchoProvider()
        router = IntelligenceRouter([cloud, local], manager)

        selected = router.select(Task(task_id="PI-004-C", prompt="fallback"))
        self.assertEqual(selected.name, "local")

    def test_high_privacy_prefers_local(self):
        manager = ResourceManager()
        cloud = SimulatedCloudProvider()
        local = EchoProvider()
        router = IntelligenceRouter([cloud, local], manager)

        selected = router.select(
            Task(task_id="PI-004-D", prompt="private", privacy="high")
        )
        self.assertEqual(selected.name, "local")


if __name__ == "__main__":
    unittest.main()
