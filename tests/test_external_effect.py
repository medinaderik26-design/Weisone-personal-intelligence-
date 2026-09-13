from core.external_effect import ExternalEffectReceipt, ExternalEffectRegistry, make_provider_acceptance


def test_provider_acceptance_is_not_external_confirmation():
    receipt = make_provider_acceptance("intent-1", "task-1", "send", "synthetic-target", "provider-123")
    registry = ExternalEffectRegistry()
    registry.record(receipt)
    assert receipt.status == "accepted"
    assert registry.confirmed("intent-1") is False


def test_external_confirmation_is_explicit():
    registry = ExternalEffectRegistry()
    receipt = ExternalEffectReceipt(
        intent_id="intent-1",
        task_id="task-1",
        operation="send",
        target="synthetic-target",
        status="confirmed",
        provider_reference="provider-123",
        evidence_source="external_confirmed",
    )
    registry.record(receipt)
    assert registry.confirmed("intent-1") is True


def test_unknown_status_is_not_treated_as_success():
    registry = ExternalEffectRegistry()
    receipt = ExternalEffectReceipt(
        intent_id="intent-2",
        task_id="task-2",
        operation="send",
        target="synthetic-target",
        status="unknown",
    )
    registry.record(receipt)
    assert registry.confirmed("intent-2") is False


def test_invalid_effect_status_rejected():
    receipt = ExternalEffectReceipt(
        intent_id="intent-3",
        task_id="task-3",
        operation="send",
        target="synthetic-target",
        status="completed",
    )
    try:
        receipt.validate()
        assert False
    except ValueError:
        pass
