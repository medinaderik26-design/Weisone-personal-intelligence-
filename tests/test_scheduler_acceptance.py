from datetime import datetime, timezone

import pytest

from core.durable_recovery_dispatch import SQLiteRecoveryDispatchStore
from core.policy_dispatch_bridge import PolicyDispatchBridge
from core.policy_dispatch_claim import PolicyDispatchClaimAdapter
from core.durable_claim_handoff import DurableClaimHandoff
from core.scheduler_acceptance import SchedulerAcceptanceBoundary
from core.scheduler_receipt import SQLiteSchedulerReceiptStore


def make_handoff(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    request = PolicyDispatchBridge().build(
        type("Boundary", (), {
            "task_id": "task-1",
            "action": "continue",
            "handoff_allowed": True,
            "reason": "allowed",
        })(),
        "expected_progression",
    )
    claim = PolicyDispatchClaimAdapter(dispatch).claim(request)
    handoff = DurableClaimHandoff(receipts).prepare(claim, intent_id="intent-1")
    return dispatch, receipts, handoff


def test_acceptance_requires_handoff_receipt(tmp_path):
    dispatch = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    request = type("Request", (), {
        "task_id": "task-1",
        "dispatch_key": "dispatch-1",
        "intent_id": "intent-1",
        "eligible": True,
    })()

    with pytest.raises(ValueError):
        SchedulerAcceptanceBoundary(receipts).accept(request)

    dispatch.close()
    receipts.close()


def test_handoff_can_be_accepted(tmp_path):
    dispatch, receipts, handoff = make_handoff(tmp_path)
    boundary = DurableClaimHandoff(receipts)
    boundary.record_handoff(handoff, now=datetime(2026, 9, 13, tzinfo=timezone.utc))

    result = SchedulerAcceptanceBoundary(receipts).accept(
        handoff,
        now=datetime(2026, 9, 13, 0, 1, tzinfo=timezone.utc),
    )

    assert result.accepted is True
    assert result.receipt is not None
    assert result.receipt.state == "accepted"
    dispatch.close()
    receipts.close()


def test_acceptance_is_idempotent(tmp_path):
    dispatch, receipts, handoff = make_handoff(tmp_path)
    boundary = DurableClaimHandoff(receipts)
    boundary.record_handoff(handoff)
    acceptance = SchedulerAcceptanceBoundary(receipts)

    first = acceptance.accept(handoff)
    second = acceptance.accept(handoff)

    assert first.accepted is True
    assert second.accepted is True
    assert second.reason == "scheduler acceptance was already durably recorded"
    dispatch.close()
    receipts.close()


def test_ineligible_handoff_is_blocked(tmp_path):
    receipts = SQLiteSchedulerReceiptStore(str(tmp_path / "receipts.sqlite"))
    request = type("Request", (), {
        "task_id": "task-1",
        "dispatch_key": "dispatch-1",
        "intent_id": "intent-1",
        "eligible": False,
    })()

    result = SchedulerAcceptanceBoundary(receipts).accept(request)
    assert result.accepted is False
    receipts.close()
