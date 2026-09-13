from datetime import datetime, timezone

from core.durable_claim_handoff import DurableClaimHandoff
from core.durable_recovery_dispatch import SQLiteRecoveryDispatchStore
from core.policy_dispatch_bridge import PolicyDispatchBridge
from core.policy_dispatch_claim import PolicyDispatchClaimAdapter
from core.scheduler_receipt import SQLiteSchedulerReceiptStore


def make_request():
    boundary = type("Boundary", (), {
        "task_id": "task-1",
        "action": "continue",
        "handoff_allowed": True,
        "reason": "allowed",
    })()
    return PolicyDispatchBridge().build(boundary, "expected_progression")


def test_durable_claim_can_prepare_handoff(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    result = PolicyDispatchClaimAdapter(dispatch).claim(make_request())

    handoff = DurableClaimHandoff(receipts)
    request = handoff.prepare(result, intent_id="intent-1")

    assert request.eligible is True
    assert request.task_id == "task-1"
    assert request.intent_id == "intent-1"
    assert request.dispatch_key == result.dispatch_key
    dispatch.close()
    receipts.close()


def test_handoff_records_only_handoff_evidence(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    result = PolicyDispatchClaimAdapter(dispatch).claim(make_request())
    handoff = DurableClaimHandoff(receipts)
    request = handoff.prepare(result, intent_id="intent-1")

    receipt = handoff.record_handoff(
        request,
        now=datetime(2026, 9, 13, tzinfo=timezone.utc),
    )

    assert receipt.state == "handed_off"
    assert receipts.get(request.dispatch_key).state == "handed_off"
    dispatch.close()
    receipts.close()


def test_duplicate_or_blocked_claim_cannot_handoff(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    adapter = PolicyDispatchClaimAdapter(dispatch)
    req = make_request()
    first = adapter.claim(req)
    duplicate = adapter.claim(req)
    handoff = DurableClaimHandoff(receipts)

    assert handoff.prepare(duplicate, intent_id="intent-1").eligible is False

    blocked = type(first)(
        task_id=first.task_id,
        dispatch_key=first.dispatch_key,
        claimed=False,
        reason="blocked",
        claim=None,
    )
    assert handoff.prepare(blocked, intent_id="intent-1").eligible is False
    dispatch.close()
    receipts.close()


def test_handoff_requires_intent_identity(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    result = PolicyDispatchClaimAdapter(dispatch).claim(make_request())
    handoff = DurableClaimHandoff(receipts)

    try:
        handoff.prepare(result)
        assert False, "expected ValueError"
    except ValueError:
        pass
    finally:
        dispatch.close()
        receipts.close()
