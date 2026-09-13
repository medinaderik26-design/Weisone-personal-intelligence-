from core.action_ledger import ActionLedgerEntry
from core.lifecycle_projection import LifecycleProjector
from datetime import datetime, timezone


def entry(task, intent, stage):
    return ActionLedgerEntry(task, intent, "send_email", "recipient", stage, stage, datetime.now(timezone.utc))


def test_projection_reconstructs_known_chain():
    entries = (
        entry("t1", "i1", "authorized"),
        entry("t1", "i1", "handed_off"),
        entry("t1", "i1", "accepted"),
        entry("t1", "i1", "executing"),
        entry("t1", "i1", "provider_accepted"),
    )
    projection = LifecycleProjector().project("t1", entries)
    assert projection.stages == ("authorized", "handed_off", "accepted", "executing", "provider_accepted")
    assert projection.current_stage == "provider_accepted"
    assert projection.evidence_complete is False


def test_external_confirmation_completes_evidence_chain():
    entries = (entry("t1", "i1", "externally_confirmed"),)
    projection = LifecycleProjector().project("t1", entries)
    assert projection.evidence_complete is True


def test_mixed_execution_intents_are_rejected():
    entries = (entry("t1", "i1", "authorized"), entry("t1", "i2", "handed_off"))
    try:
        LifecycleProjector().project("t1", entries)
    except ValueError:
        pass
    else:
        raise AssertionError("expected multiple-intent rejection")
