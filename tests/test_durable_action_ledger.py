from datetime import datetime, timezone

import pytest

from core.action_ledger import ActionLedgerEntry
from core.durable_action_ledger import SQLiteActionLedger


def entry(stage):
    return ActionLedgerEntry(
        task_id="task-1",
        intent_id="intent-1",
        operation="send_email",
        target="synthetic@example.test",
        stage=stage,
        statement=f"stage={stage}",
        timestamp=datetime.now(timezone.utc),
    )


def test_ledger_survives_reopen(tmp_path):
    path = str(tmp_path / "ledger.db")
    ledger = SQLiteActionLedger(path)
    ledger.append(entry("planned"))
    ledger.append(entry("confirmed"))
    ledger.close()

    recovered = SQLiteActionLedger(path)
    entries = recovered.for_task("task-1")
    assert [e.stage for e in entries] == ["planned", "confirmed"]
    recovered.close()


def test_invalid_transition_is_rejected(tmp_path):
    ledger = SQLiteActionLedger(str(tmp_path / "ledger.db"))
    ledger.append(entry("planned"))
    with pytest.raises(ValueError):
        ledger.append(entry("externally_confirmed"))
    ledger.close()


def test_identity_cannot_change_after_restart(tmp_path):
    path = str(tmp_path / "ledger.db")
    ledger = SQLiteActionLedger(path)
    ledger.append(entry("planned"))
    ledger.close()

    recovered = SQLiteActionLedger(path)
    changed = ActionLedgerEntry(
        task_id="task-1",
        intent_id="different-intent",
        operation="send_email",
        target="synthetic@example.test",
        stage="confirmed",
        statement="stage=confirmed",
        timestamp=datetime.now(timezone.utc),
    )
    with pytest.raises(ValueError):
        recovered.append(changed)
    recovered.close()
