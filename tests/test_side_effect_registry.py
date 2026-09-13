import pytest

from core.side_effect_registry import SideEffectProfile, SideEffectRegistry


def test_registered_cancelable_operation_is_allowed():
    registry = SideEffectRegistry()
    profile = SideEffectProfile("send_email", cancelable=True, reversible=False, compensatable=False)
    registry.register(profile)
    assert registry.get("send_email") == profile


def test_irreversible_operation_requires_confirmation():
    registry = SideEffectRegistry()
    with pytest.raises(ValueError):
        registry.register(SideEffectProfile("irreversible", False, False, False))


def test_irreversible_confirmed_operation_can_be_registered():
    registry = SideEffectRegistry()
    profile = SideEffectProfile("publish", False, False, False, requires_confirmation=True)
    registry.register(profile)
    assert registry.contains("publish") is True


def test_unknown_operation_is_not_assumed_safe():
    registry = SideEffectRegistry()
    with pytest.raises(KeyError):
        registry.get("unknown")
