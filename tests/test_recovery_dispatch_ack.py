import pytest

from core.recovery_dispatch_ack import DispatchAcknowledgement, DispatchAcknowledgementPolicy


def test_acknowledgement_validates():
    record = DispatchAcknowledgement("task-1", "key-1", "claimed", "claim recorded")
    record.validate()


def test_acknowledgement_requires_ordered_progression():
    policy = DispatchAcknowledgementPolicy()
    assert policy.can_transition("claimed", "handed_off")
    assert policy.can_transition("handed_off", "accepted")
    assert not policy.can_transition("claimed", "accepted")


def test_invalid_transition_is_rejected():
    with pytest.raises(ValueError):
        DispatchAcknowledgementPolicy().require_transition("accepted", "handed_off")
