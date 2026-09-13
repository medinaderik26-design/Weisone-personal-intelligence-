from core.ledger_scheduler_validator import SchedulerLedgerValidator


def test_handoff_requires_authorization():
    validator = SchedulerLedgerValidator()
    validator.require(("planned", "confirmed", "authorized"), "handed_off")


def test_handoff_without_authorization_is_rejected():
    validator = SchedulerLedgerValidator()
    try:
        validator.require(("planned", "confirmed"), "handed_off")
    except ValueError as exc:
        assert str(exc) == "scheduler stage 'handed_off' is missing required predecessor evidence"
    else:
        raise AssertionError("expected ValueError")


def test_acceptance_requires_handoff():
    validator = SchedulerLedgerValidator()
    validator.require(("authorized", "handed_off"), "accepted")


def test_acceptance_cannot_bypass_handoff():
    validator = SchedulerLedgerValidator()
    try:
        validator.require(("authorized",), "accepted")
    except ValueError as exc:
        assert str(exc) == "scheduler stage 'accepted' is missing required predecessor evidence"
    else:
        raise AssertionError("expected ValueError")
