import unittest

from core.continuity import InMemoryContinuity
from core.models import Identity, Task
from core.permissions import PermissionEngine
from core.providers import EchoProvider
from core.router import IntelligenceRouter
from core.runtime import PersonalIntelligence


class TestPI001(unittest.TestCase):
    def setUp(self):
        permissions = PermissionEngine.deny_all()
        permissions.grant("intelligence", "execute")
        self.continuity = InMemoryContinuity()
        self.pi = PersonalIntelligence(
            identity=Identity(person_id="test-person"),
            permissions=permissions,
            router=IntelligenceRouter([EchoProvider()]),
            continuity=self.continuity,
        )

    def test_core_loop(self):
        record = self.pi.execute(
            Task(task_id="PI-001", prompt="hello personal intelligence")
        )
        self.assertTrue(record.result.success)
        self.assertEqual(record.result.provider, "local")
        self.assertTrue(record.continuity_updated)
        self.assertEqual(len(self.continuity.events), 1)

    def test_permission_boundary(self):
        pi = PersonalIntelligence(
            identity=Identity(person_id="test-person"),
            permissions=PermissionEngine.deny_all(),
            router=IntelligenceRouter([EchoProvider()]),
            continuity=self.continuity,
        )
        with self.assertRaises(PermissionError):
            pi.execute(Task(task_id="PI-002", prompt="should fail"))


if __name__ == "__main__":
    unittest.main()
