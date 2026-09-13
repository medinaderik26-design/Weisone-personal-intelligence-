import unittest

from core.ollama_provider import OllamaProvider, OllamaResponse
from core.v01_execution_slice import PersonalIntelligenceSlice


class OllamaProviderTests(unittest.TestCase):
    def test_ollama_provider_preserves_v01_slice_semantics(self):
        calls = []

        def request(url, body):
            calls.append((url, body))
            if url.endswith("/api/tags"):
                return OllamaResponse(200, {"models": [{"name": "test-model"}]})
            return OllamaResponse(200, {"response": "local model response"})

        provider = OllamaProvider("test-model", request=request)
        result = PersonalIntelligenceSlice(provider).execute("ollama-work-001", "hello")

        self.assertEqual(result.proposal.status, "accepted")
        self.assertTrue(result.run.success)
        self.assertEqual(result.run.output, "local model response")
        self.assertTrue(result.evidence.verified)
        self.assertEqual(result.evidence.work_id, "ollama-work-001")
        self.assertEqual(result.continuity.open_work_ids, [])
        self.assertEqual([url.rsplit("/", 1)[-1] for url, _ in calls], ["tags", "generate"])

    def test_unavailable_ollama_is_rejected_before_run(self):
        run_calls = []

        def request(url, body):
            if url.endswith("/api/tags"):
                raise OSError("connection refused")
            run_calls.append(url)
            return OllamaResponse(200, {"response": "should not run"})

        provider = OllamaProvider("test-model", request=request)
        result = PersonalIntelligenceSlice(provider).execute("ollama-work-002", "hello")

        self.assertEqual(result.proposal.status, "rejected")
        self.assertIsNone(result.run)
        self.assertEqual(run_calls, [])
        self.assertIn("ollama-work-002", result.continuity.open_work_ids)

    def test_http_failure_does_not_claim_execution_success(self):
        def request(url, body):
            if url.endswith("/api/tags"):
                return OllamaResponse(200, {"models": [{"name": "test-model"}]})
            return OllamaResponse(500, {})

        provider = OllamaProvider("test-model", request=request)
        result = PersonalIntelligenceSlice(provider).execute("ollama-work-003", "hello")

        self.assertEqual(result.proposal.status, "accepted")
        self.assertFalse(result.run.success)
        self.assertIsNone(result.evidence)
        self.assertIn("ollama-work-003", result.continuity.open_work_ids)

    def test_missing_response_text_does_not_verify(self):
        def request(url, body):
            if url.endswith("/api/tags"):
                return OllamaResponse(200, {"models": [{"name": "test-model"}]})
            return OllamaResponse(200, {"model": "test-model"})

        provider = OllamaProvider("test-model", request=request)
        result = PersonalIntelligenceSlice(provider).execute("ollama-work-004", "hello")

        self.assertFalse(result.run.success)
        self.assertIsNone(result.evidence)
        self.assertIn("ollama-work-004", result.continuity.open_work_ids)


if __name__ == "__main__":
    unittest.main()
