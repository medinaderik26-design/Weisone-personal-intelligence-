import pytest

from core.external_effect_bridge import ExternalEffectVerificationBridge
from core.provider_acceptance import ProviderAcceptanceResult


def provider(accepted=True):
    return ProviderAcceptanceResult(
        task_id="task-1",
        dispatch_key="dispatch-1",
        intent_id="intent-1",
        provider="echo",
        accepted=accepted,
        recorded_at="2026-09-13T00:00:00+00:00",
        reason="test",
    )


def test_provider_acceptance_creates_verification_request():
    request = ExternalEffectVerificationBridge().build(
        provider(),
        operation="send_message",
        target="example-target",
    )

    assert request.eligible is True
    assert request.operation == "send_message"
    assert request.target == "example-target"


def test_provider_rejection_blocks_external_verification():
    request = ExternalEffectVerificationBridge().build(
        provider(False),
        operation="send_message",
        target="example-target",
    )

    assert request.eligible is False
    assert "provider acceptance" in request.reason


def test_missing_operation_or_target_is_rejected():
    bridge = ExternalEffectVerificationBridge()

    with pytest.raises(ValueError):
        bridge.build(provider(), operation="", target="example-target")

    with pytest.raises(ValueError):
        bridge.build(provider(), operation="send_message", target="")
