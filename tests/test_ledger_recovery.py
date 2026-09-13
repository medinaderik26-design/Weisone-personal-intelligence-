from datetime import datetime, timezone

from core.action_ledger import ActionLedgerEntry
from core.durable_action_ledger import SQLiteActionLedger
from core.ledger_recovery import ActionLedgerRecovery
from core.persistent_work_state import WorkState


def entry(stage, task="task-1", intent="intent-1"):
    return ActionLedgerEntry(
        task_id=task,
        intent_id=intent,
        operation="send_email",
        target="synthetic@example.test",
        stage=stage,
        statement=stage,
        timestamp=datetime.now(timezone.utc),
    )


def test_externally_confirmed_work_is_reconciled_as_complete(tmp_path):
    ledger = SQLiteActionLedger(str(tmp_path / "ledger.db"))
    ledger.append(entry("planned"))
    ledger.append(entry("confirmed"))
    ledger.append(entry("authorized"))
    ledger.append(entry("executing"))
    ledger.append(entry("provider_accepted"))
    ledger.append(entry("externally_confirmed"))

    decision = ActionLedgerRecovery(ledger).inspect(WorkState("task-1", "running"))
    assert decision.action == "complete"
    assert decision.intent_id == "intent-1"
    ledger.close()


def test_provider_accepted_requires_external_verification(tmp_path):
    ledger = SQLiteActionLedger(str(tmp_path / "ledger.db"))
    ledger.append(entry("planned"))
    ledger.append(entry("confirmed"))
    ledger.append(entry("authorized"))
    ledger.append(entry("executing"))
    ledger.append(entry("provider_accepted"))

    decision = ActionLedgerRecovery(ledger).inspect(WorkState("task-1", "running"))
    assert decision.action == "verify_external_effect"
    ledger.close()


def test_missing_history_for_running_work_requires_review(tmp_path):
    ledger = SQLiteActionLedger(str(tmp_path / "ledger.db"))
    decision = ActionLedgerRecovery(ledger).inspect(WorkState("task-1", "running"))
    assert decision.action == "human_review"
    ledger.close()


def test_failed_work_can_enter_retry_or_reroute_path(tmp_path):
    ledger = SQLiteActionLedger(str(tmp_path / "ledger.db"))
    ledger.append(entry("planned"))
    ledger.append(entry("confirmed"))
    ledger.append(entry("authorized"))
    ledger.append(entry("executing"))
    ledger.append(entry("failed"))

    decision = ActionLedgerRecovery(ledger).inspect(WorkState("task-1", "failed"))
    assert decision.action == "retry_or_reroute"
    ledger.close()
