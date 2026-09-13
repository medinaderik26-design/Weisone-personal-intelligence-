import unittest

from core.models import Task
from core.providers import EchoProvider
from core.resource_manager import ResourceManager
from core.router import IntelligenceRouter


class TestPI003(unittest.TestCase):
    def setUp(self):
        self.resources = ResourceManager()
        self.local = EchoProvider()
        self.router = IntelligenceRouter([self.local], self.resources)

    def test_router_uses_available_provider(self):
        provider = self.router.select(Task(task_id="PI-003-A", prompt="hello"))
        self.assertIs(provider, self.local)

    def test_router_denies_exhausted_provider(self):
        snapshot = self.resources.snapshot("local")
        snapshot.requests_limit = 1
        snapshot.requests_used = 1

        with self.assertRaises(RuntimeError):
            self.router.select(Task(task_id="PI-003-B", prompt="hello"))

    def test_high_privacy_prefers_local(self):
        provider = self.router.select(
            Task(task_id="PI-003-C", prompt="private", privacy="high")
        )
        self.assertEqual(provider.name, "local")


if __name__ == "__main__":
    unittest.main()
