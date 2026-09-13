from core.ledger_scheduler_bridge import LedgerSchedulerBridge
from core.scheduler_receipt import SchedulerReceipt


def test_handoff_receipt_becomes_ledger_evidence():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "handed_off", "2026-09-13T00:00:00+00:00")
    entry = LedgerSchedulerBridge().entry_from_receipt(receipt, "send_email", "recipient")
    assert entry.stage == "handed_off"
    assert entry.intent_id == "intent-1"


def test_acceptance_receipt_does_not_claim_execution():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "2026-09-13T00:00:00+00:00")
    entry = LedgerSchedulerBridge().entry_from_receipt(receipt, "send_email", "recipient")
    assert entry.stage == "accepted"
    assert "execution outcome remains unconfirmed" in entry.statement
