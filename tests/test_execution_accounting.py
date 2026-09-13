import unittest

from core.execution_accounting import AccountedExecution
from core.models import Task
from core.providers import EchoProvider
from core.resource_manager import ResourceManager


class TestExecutionAccounting(unittest.TestCase):
    def test_successful_execution_is_recorded(self):
        manager = ResourceManager()
        manager.register_provider("local", model="echo-v0.1")
        executor = AccountedExecution(manager)

        result = executor.run(
            EchoProvider(),
            Task(task_id="PI-005", prompt="account this request"),
        )

        self.assertTrue(result.success)
        snapshot = manager.snapshot("local")
        self.assertEqual(snapshot.requests_used, 1)
        self.assertGreaterEqual(snapshot.latency_ms, 0)

    def test_usage_is_recorded_when_provider_reports_it(self):
        class UsageProvider(EchoProvider):
            def generate(self, task):
                result = super().generate(task)
                result.usage = {
                    "input_tokens": 12,
                    "output_tokens": 7,
                    "estimated_cost": 0.03,
                }
                return result

        manager = ResourceManager()
        manager.register_provider("local", model="usage-test")
        executor = AccountedExecution(manager)
        executor.run(UsageProvider(), Task(task_id="PI-005-B", prompt="usage"))

        snapshot = manager.snapshot("local")
        self.assertEqual(snapshot.input_tokens, 12)
        self.assertEqual(snapshot.output_tokens, 7)
        self.assertEqual(snapshot.estimated_cost, 0.03)


if __name__ == "__main__":
    unittest.main()
