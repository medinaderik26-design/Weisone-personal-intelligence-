from core.effect_verification import EffectVerificationRegistry, ExplicitConfirmationVerifier
from core.external_effect import ExternalEffectReceipt


def receipt(effect_id="intent-1"):
    return ExternalEffectReceipt(
        intent_id=effect_id,
        task_id="task-1",
        operation="send_email",
        target="synthetic@example.test",
        status="confirmed",
        evidence_source="external_confirmed",
    )


def test_registered_verifier_confirms_known_external_effect():
    registry = EffectVerificationRegistry()
    registry.register("send_email", ExplicitConfirmationVerifier({"intent-1"}))
    result = registry.verify("send_email", receipt())
    assert result.verified is True


def test_registered_verifier_rejects_unconfirmed_effect():
    registry = EffectVerificationRegistry()
    registry.register("send_email", ExplicitConfirmationVerifier())
    result = registry.verify("send_email", receipt())
    assert result.verified is False


def test_unknown_operation_has_no_verification_policy():
    result = EffectVerificationRegistry().verify("unknown", receipt())
    assert result.verified is False
    assert "no verification policy" in result.reason
