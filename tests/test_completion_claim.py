from core.completion_claim import CompletionClaimPolicy
from core.evidence_confidence import EvidenceConfidence


def test_no_evidence_cannot_claim_completion():
    claim = CompletionClaimPolicy().claim(EvidenceConfidence(0.0, "none", "no evidence"))
    assert claim.level == "not_completed"
    assert "cannot confirm" in claim.statement


def test_provider_acceptance_is_not_external_completion():
    claim = CompletionClaimPolicy().claim(EvidenceConfidence(0.5, "moderate", "provider accepted"))
    assert claim.level == "provider_accepted"
    assert "not independently confirmed" in claim.statement


def test_external_confirmation_allows_completion_claim():
    claim = CompletionClaimPolicy().claim(EvidenceConfidence(0.9, "strong", "external confirmed"))
    assert claim.level == "externally_confirmed"
    assert "confirmed" in claim.statement
