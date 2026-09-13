from core.ledger_lifecycle import LedgerLifecycleValidator


def test_normal_execution_transition_is_allowed():
    result = LedgerLifecycleValidator().check("executing", "provider_accepted")
    assert result.allowed is True


def test_provider_acceptance_can_become_external_confirmation():
    result = LedgerLifecycleValidator().check("provider_accepted", "externally_confirmed")
    assert result.allowed is True


def test_completed_effect_cannot_go_back_to_planned():
    result = LedgerLifecycleValidator().check("externally_confirmed", "planned")
    assert result.allowed is False


def test_retry_path_is_explicit():
    result = LedgerLifecycleValidator().check("failed", "retrying")
    assert result.allowed is True


def test_unknown_stage_is_rejected():
    result = LedgerLifecycleValidator().check("unknown", "executing")
    assert result.allowed is False
