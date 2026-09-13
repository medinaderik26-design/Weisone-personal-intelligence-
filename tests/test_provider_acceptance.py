from datetime import datetime, timezone

import pytest

from core.execution_start import ExecutionStartRecord
from core.provider_acceptance import ProviderAcceptanceBoundary


def execution(started=True):
    return ExecutionStartRecord(
        task_id="task-1",
        dispatch_key="dispatch-1",
        intent_id="intent-1",
        started=started,
        recorded_at=datetime(2026, 9, 13, tzinfo=timezone.utc).isoformat(),
        reason="test",
    )


def test_started_execution_can_record_provider_acceptance():
    result = ProviderAcceptanceBoundary().accept(
        execution(),
        provider="echo",
        accepted=True,
    )

    assert result.accepted is True
    assert result.provider == "echo"


def test_unstarted_execution_cannot_be_provider_accepted():
    result = ProviderAcceptanceBoundary().accept(
        execution(False),
        provider="echo",
        accepted=True,
    )

    assert result.accepted is False
    assert "execution has not started" in result.reason


def test_provider_rejection_is_recorded_without_being_completion():
    result = ProviderAcceptanceBoundary().accept(
        execution(),
        provider="echo",
        accepted=False,
    )

    assert result.accepted is False
    assert "did not accept" in result.reason


def test_required_identity_is_validated():
    boundary = ProviderAcceptanceBoundary()
    bad = ExecutionStartRecord("", "dispatch-1", "intent-1", True, "now", "test")

    with pytest.raises(ValueError):
        boundary.accept(bad, provider="echo", accepted=True)
