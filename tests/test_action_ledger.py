from core.action_ledger import ActionLedger, ActionLedgerEntry


def test_ledger_preserves_task_and_intent_history():
    ledger = ActionLedger()
    ledger.record(
        task_id="task-1",
        intent_id="intent-1",
        operation="send_email",
        target="synthetic@example.test",
        stage="confirmed",
        statement="User confirmed the planned action.",
    )
    ledger.record(
        task_id="task-1",
        intent_id="intent-1",
        operation="send_email",
        target="synthetic@example.test",
        stage="externally_confirmed",
        statement="External system confirmed the effect.",
        confidence=0.9,
    )

    assert len(ledger.for_task("task-1")) == 2
    assert len(ledger.for_intent("intent-1")) == 2
    assert ledger.for_intent("intent-1")[-1].confidence == 0.9


def test_invalid_confidence_rejected():
    entry = ActionLedgerEntry(
        task_id="task-1",
        intent_id="intent-1",
        operation="op",
        target="target",
        stage="stage",
        statement="statement",
        timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        confidence=1.1,
    )
    try:
        entry.validate()
        assert False
    except ValueError:
        pass
