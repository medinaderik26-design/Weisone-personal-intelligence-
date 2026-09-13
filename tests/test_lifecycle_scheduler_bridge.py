from core.lifecycle_scheduler_bridge import LifecycleSchedulerBridge
from core.scheduler_receipt import SchedulerReceipt


def test_handoff_requires_authorized_predecessor():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "handed_off", "2026-09-13T00:00:00+00:00")
    entry = LifecycleSchedulerBridge().entry_from_receipt(
        receipt, "send_email", "recipient", ("planned", "confirmed", "authorized")
    )
    assert entry.stage == "handed_off"


def test_handoff_cannot_bypass_authorization():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "handed_off", "2026-09-13T00:00:00+00:00")
    try:
        LifecycleSchedulerBridge().entry_from_receipt(receipt, "send_email", "recipient", ("planned", "confirmed"))
    except ValueError:
        pass
    else:
        raise AssertionError("expected lifecycle validation failure")


def test_acceptance_requires_handoff():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "2026-09-13T00:00:00+00:00")
    entry = LifecycleSchedulerBridge().entry_from_receipt(
        receipt, "send_email", "recipient", ("planned", "confirmed", "authorized", "handed_off")
    )
    assert entry.stage == "accepted"


def test_acceptance_cannot_bypass_handoff():
    receipt = SchedulerReceipt("task-1", "intent-1", "dispatch-1", "accepted", "2026-09-13T00:00:00+00:00")
    try:
        LifecycleSchedulerBridge().entry_from_receipt(
            receipt, "send_email", "recipient", ("planned", "confirmed", "authorized")
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected lifecycle validation failure")
