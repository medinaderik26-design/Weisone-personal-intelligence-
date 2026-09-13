import pytest

from core.confirmation_gate import ConfirmationGate
from core.side_effect_registry import SideEffectProfile


def test_consequential_operation_requires_confirmation():
    profile = SideEffectProfile(
        "publish", cancelable=False, reversible=False, compensatable=False,
        requires_confirmation=True,
    )
    gate = ConfirmationGate()
    request = gate.request("t1", profile)
    result = gate.decide(request, confirmed=False)
    assert result.allowed is False


def test_confirmation_allows_consequential_operation():
    profile = SideEffectProfile(
        "publish", cancelable=False, reversible=False, compensatable=False,
        requires_confirmation=True,
    )
    request = ConfirmationGate().request("t2", profile)
    result = ConfirmationGate().decide(request, confirmed=True)
    assert result.allowed is True
    assert result.reason == "explicit confirmation received"


def test_non_consequential_operation_does_not_need_confirmation():
    profile = SideEffectProfile("draft", cancelable=True, reversible=True, compensatable=False)
    request = ConfirmationGate().request("t3", profile)
    result = ConfirmationGate().decide(request, confirmed=False)
    assert result.allowed is True


def test_task_id_required():
    profile = SideEffectProfile("publish", False, False, False, requires_confirmation=True)
    with pytest.raises(ValueError):
        ConfirmationGate().request("", profile)
