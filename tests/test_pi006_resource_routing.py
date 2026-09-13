import unittest

from core.models import Task
from core.providers import EchoProvider, SimulatedCloudProvider
from core.resource_manager import ResourceManager
from core.resource_router import ResourceAwareRouter


class TestPI006ResourceRouting(unittest.TestCase):
    def test_remaining_quota_can_break_a_tie(self):
        manager = ResourceManager()
        cloud = SimulatedCloudProvider(requests_limit=10)
        local = EchoProvider()
        router = ResourceAwareRouter([cloud, local], manager)

        selected = router.select(Task(task_id="PI-006-A", prompt="work"))
        self.assertEqual(selected.name, "cloud-sim")

    def test_high_privacy_still_prefers_local(self):
        manager = ResourceManager()
        cloud = SimulatedCloudProvider(requests_limit=100)
        local = EchoProvider()
        router = ResourceAwareRouter([cloud, local], manager)

        selected = router.select(
            Task(task_id="PI-006-B", prompt="private", privacy="high")
        )
        self.assertEqual(selected.name, "local")

    def test_low_latency_prefers_provider_with_observed_latency(self):
        manager = ResourceManager()
        cloud = SimulatedCloudProvider(requests_limit=10)
        local = EchoProvider()
        router = ResourceAwareRouter([cloud, local], manager)

        manager.record_request("cloud-sim", latency_ms=5.0)
        manager.record_request("local", latency_ms=40.0)

        selected = router.select(
            Task(task_id="PI-006-C", prompt="fast", latency="low")
        )
        self.assertEqual(selected.name, "cloud-sim")


if __name__ == "__main__":
    unittest.main()
