import unittest

from core.models import Task
from core.performance_router import PerformanceAwareRouter
from core.providers import SimulatedCloudProvider
from core.resource_manager import ResourceManager
from core.task_performance import TaskPerformanceRegistry


class TestPerformanceAwareRouter(unittest.TestCase):
    def test_measured_quality_can_prefer_provider_for_task_type(self):
        local = SimulatedCloudProvider(name="local", model="local-model")
        cloud = SimulatedCloudProvider(name="cloud", model="cloud-model")
        resources = ResourceManager()
        resources.register_provider("local", model="local-model", requests_limit=10)
        resources.register_provider("cloud", model="cloud-model", requests_limit=10)

        history = TaskPerformanceRegistry()
        history.record("local", "coding", success=True, quality=0.7)
        history.record("cloud", "coding", success=True, quality=0.95)

        router = PerformanceAwareRouter([local, cloud], resources, history)
        task = Task(task_id="t1", prompt="write code", metadata={"task_type": "coding"})

        self.assertEqual(router.select(task).name, "cloud")

    def test_high_privacy_remains_a_hard_constraint(self):
        local = SimulatedCloudProvider(name="local", model="local-model")
        cloud = SimulatedCloudProvider(name="cloud", model="cloud-model")
        resources = ResourceManager()
        resources.register_provider("local", model="local-model", requests_limit=10)
        resources.register_provider("cloud", model="cloud-model", requests_limit=10)

        history = TaskPerformanceRegistry()
        history.record("cloud", "research", success=True, quality=1.0)

        router = PerformanceAwareRouter([local, cloud], resources, history)
        task = Task(task_id="t2", prompt="private notes", privacy="high", metadata={"task_type": "research"})

        self.assertEqual(router.select(task).name, "local")


if __name__ == "__main__":
    unittest.main()
