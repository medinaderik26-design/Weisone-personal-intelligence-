from datetime import datetime, timezone

import pytest

from core.action_ledger import ActionLedgerEntry
from core.lifecycle_ledger import LifecycleActionLedger


def entry(stage, intent="intent-1", task="task-1"):
    return ActionLedgerEntry(
        task_id=task,
        intent_id=intent,
        operation="send_email",
        target="synthetic@example.test",
        stage=stage,
        statement=f"stage={stage}",
        timestamp=datetime.now(timezone.utc),
    )


def test_append_enforces_valid_transition():
    ledger = LifecycleActionLedger()
    ledger.append(entry("planned"))
    ledger.append(entry("confirmed"))
    ledger.append(entry("authorized"))
    assert [x.stage for x in ledger.for_task("task-1")] == ["planned", "confirmed", "authorized"]


def test_append_rejects_impossible_transition():
    ledger = LifecycleActionLedger()
    ledger.append(entry("planned"))
    with pytest.raises(ValueError):
        ledger.append(entry("externally_confirmed"))


def test_append_rejects_identity_change():
    ledger = LifecycleActionLedger()
    ledger.append(entry("planned"))
    with pytest.raises(ValueError):
        ledger.append(entry("confirmed", intent="different-intent"))
