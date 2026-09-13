import unittest

from core.performance_confidence import ConfidencePolicy, PerformanceConfidence, PerformanceEvidence


class TestPerformanceConfidence(unittest.TestCase):
    def test_sparse_evidence_is_not_reliable(self):
        gate = PerformanceConfidence(ConfidencePolicy(min_samples=3, min_quality_samples=3))
        evidence = PerformanceEvidence("cloud", "coding", 2, 1.0, 0.95, 2)
        self.assertFalse(gate.is_reliable(evidence))
        self.assertIsNone(gate.score(evidence))

    def test_reliable_evidence_can_receive_score(self):
        gate = PerformanceConfidence(ConfidencePolicy(min_samples=3, min_quality_samples=3))
        evidence = PerformanceEvidence("cloud", "coding", 5, 0.8, 0.9, 5)
        self.assertTrue(gate.is_reliable(evidence))
        self.assertEqual(gate.score(evidence), 0.9)

    def test_quality_is_required_for_reliable_quality_score(self):
        gate = PerformanceConfidence()
        evidence = PerformanceEvidence("cloud", "coding", 10, 1.0, None, 0)
        self.assertFalse(gate.is_reliable(evidence))


if __name__ == "__main__":
    unittest.main()
