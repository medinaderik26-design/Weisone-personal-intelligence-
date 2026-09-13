from datetime import datetime, timezone

import pytest

from core.execution_start import ExecutionStartBoundary
from core.scheduler_acceptance import SchedulerAcceptanceResult


def acceptance(accepted=True):
    return SchedulerAcceptanceResult(
        task_id="task-1",
        dispatch_key="dispatch-1",
        intent_id="intent-1",
        accepted=accepted,
        reason="test",
    )


def test_accepted_scheduler_allows_execution_start():
    result = ExecutionStartBoundary().start(
        acceptance(True),
        now=datetime(2026, 9, 13, tzinfo=timezone.utc),
    )

    assert result.started is True
    assert result.task_id == "task-1"
    assert result.intent_id == "intent-1"


def test_unaccepted_scheduler_blocks_execution_start():
    result = ExecutionStartBoundary().start(acceptance(False))

    assert result.started is False
    assert "scheduler acceptance" in result.reason


def test_missing_identity_is_rejected():
    boundary = ExecutionStartBoundary()
    bad = SchedulerAcceptanceResult("", "dispatch-1", "intent-1", True, "test")

    with pytest.raises(ValueError):
        boundary.start(bad)
