from core.effect_verification import VerificationResult
from core.evidence_confidence import EvidenceConfidenceModel
from core.external_effect import ExternalEffectReceipt


def make_receipt(source="external_confirmed"):
    return ExternalEffectReceipt(
        intent_id="intent-1",
        task_id="task-1",
        operation="send_email",
        target="synthetic@example.test",
        status="confirmed",
        evidence_source=source,
    )


def test_unverified_evidence_has_no_confidence():
    result = EvidenceConfidenceModel().evaluate(
        make_receipt(), VerificationResult(False, "not confirmed")
    )
    assert result.score == 0.0
    assert result.level == "none"


def test_provider_acceptance_is_moderate_not_strong():
    receipt = ExternalEffectReceipt(
        intent_id="intent-1",
        task_id="task-1",
        operation="send_email",
        target="synthetic@example.test",
        status="accepted",
        evidence_source="provider_reported",
    )
    result = EvidenceConfidenceModel().evaluate(
        receipt, VerificationResult(True, "provider accepted")
    )
    assert result.level == "moderate"
    assert result.score == 0.5


def test_external_confirmation_is_strong():
    result = EvidenceConfidenceModel().evaluate(
        make_receipt(), VerificationResult(True, "externally confirmed")
    )
    assert result.level == "strong"
    assert result.score == 0.9


def test_independent_confirmation_is_strongest():
    result = EvidenceConfidenceModel().evaluate(
        make_receipt(), VerificationResult(True, "confirmed"), independent_confirmation=True
    )
    assert result.score == 1.0
