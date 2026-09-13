import unittest

from core.v01_execution_slice import PersonalIntelligenceSlice, StubProvider


class V01ExecutionSliceTests(unittest.TestCase):
    WORK_ID = "work-001"

    def test_happy_path_closes_same_work_id_and_updates_continuity(self):
        pi = PersonalIntelligenceSlice(StubProvider())
        result = pi.execute(self.WORK_ID, "send_test_message")

        self.assertTrue(result.receipt.allowed)
        self.assertEqual(result.proposal.status, "accepted")
        self.assertTrue(result.run.success)
        self.assertTrue(result.evidence.verified)
        self.assertEqual(result.evidence.work_id, self.WORK_ID)
        self.assertNotIn(self.WORK_ID, result.continuity.open_work_ids)
        self.assertEqual(result.continuity.version, 1)
        self.assertEqual(result.continuity.identity_id, "person-001")
        self.assertEqual(result.continuity.last_receipt_ids, ["receipt-1"])
        self.assertEqual(result.continuity.last_evidence_ids, ["evidence-ok"])
        self.assertEqual(
            [e["stage"] for e in pi.ledger.entries],
            ["gate", "receipt", "proposal", "run", "verify"],
        )

    def test_failure_catalog(self):
        cases = [
            ("authorization_denied", None, False, "rejected", False),
            ("provider_rejected", "reject", True, "rejected", False),
            ("confirmation_required", "needs_confirm", True, "needs_confirm", False),
            ("provider_disappears", "provider_disappears", True, "rejected", False),
            ("run_failure", "run_failure", True, "accepted", True),
            ("verification_failure", "verify_failure", True, "accepted", True),
        ]

        for name, failure, authorized, expected_proposal, should_have_run in cases:
            with self.subTest(name=name):
                provider = StubProvider(failure)
                pi = PersonalIntelligenceSlice(provider)
                result = pi.execute(self.WORK_ID, "send_test_message", authorized=authorized)

                self.assertEqual(result.proposal.status, expected_proposal)
                if should_have_run:
                    self.assertIsNotNone(result.run)
                    self.assertEqual(provider.run_count, 1)
                else:
                    self.assertIsNone(result.run)
                    self.assertEqual(provider.run_count, 0)

                if name == "confirmation_required":
                    self.assertIn(self.WORK_ID, result.continuity.open_work_ids)

    def test_needs_confirm_is_a_hard_stop_with_no_timeout_to_run(self):
        provider = StubProvider("needs_confirm")
        pi = PersonalIntelligenceSlice(provider)

        result = pi.execute(self.WORK_ID, "send_test_message")

        self.assertEqual(result.proposal.status, "needs_confirm")
        self.assertIsNone(result.run)
        self.assertEqual(provider.run_count, 0)
        self.assertIn(self.WORK_ID, result.continuity.open_work_ids)

    def test_verification_must_write_back_to_same_work_id(self):
        class WrongWorkIdProvider(StubProvider):
            def verify(self, work_id, run):
                return type("Evidence", (), {
                    "evidence_id": "evidence-wrong",
                    "work_id": "different-work",
                    "verified": True,
                    "reason": "wrong work id",
                })()

        provider = WrongWorkIdProvider()
        pi = PersonalIntelligenceSlice(provider)
        result = pi.execute(self.WORK_ID, "send_test_message")

        self.assertNotEqual(result.evidence.work_id, self.WORK_ID)
        self.assertIn(self.WORK_ID, result.continuity.open_work_ids)
        self.assertEqual(result.continuity.last_evidence_ids, [])

    def test_failed_run_leaves_work_open(self):
        provider = StubProvider("run_failure")
        pi = PersonalIntelligenceSlice(provider)

        result = pi.execute(self.WORK_ID, "send_test_message")

        self.assertFalse(result.run.success)
        self.assertIsNone(result.evidence)
        self.assertIn(self.WORK_ID, result.continuity.open_work_ids)
        self.assertEqual(result.continuity.last_receipt_ids, [])
        self.assertEqual(result.continuity.last_evidence_ids, [])

    def test_failed_verification_can_retry_and_then_close_same_work_id(self):
        provider = StubProvider("verify_failure")
        pi = PersonalIntelligenceSlice(provider)

        failed = pi.execute(self.WORK_ID, "send_test_message")
        self.assertFalse(failed.evidence.verified)
        self.assertIn(self.WORK_ID, failed.continuity.open_work_ids)

        provider.failure = None
        recovered = pi.execute(self.WORK_ID, "send_test_message")

        self.assertTrue(recovered.evidence.verified)
        self.assertEqual(recovered.evidence.work_id, self.WORK_ID)
        self.assertNotIn(self.WORK_ID, recovered.continuity.open_work_ids)
        self.assertEqual(recovered.continuity.last_receipt_ids, ["receipt-2"])
        self.assertEqual(recovered.continuity.last_evidence_ids, ["evidence-ok"])
        self.assertEqual(provider.run_count, 2)


if __name__ == "__main__":
    unittest.main()
