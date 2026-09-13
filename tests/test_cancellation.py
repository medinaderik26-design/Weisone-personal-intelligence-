import pytest

from core.cancellation import CancellationPolicy


def test_unstarted_work_can_cancel_cleanly():
    result = CancellationPolicy().decide(
        "t1", started=False, cancelable=True, external_side_effect=False, user_revoked=True
    )
    assert result.action == "cancel_before_start"


def test_started_cancelable_work_can_stop_after_revocation():
    result = CancellationPolicy().decide(
        "t2", started=True, cancelable=True, external_side_effect=False, user_revoked=True
    )
    assert result.action == "cancel"


def test_started_external_work_can_compensate_when_registered():
    result = CancellationPolicy().decide(
        "t3",
        started=True,
        cancelable=False,
        external_side_effect=True,
        compensation_available=True,
        user_revoked=True,
    )
    assert result.action == "compensate"
    assert result.compensation == "apply_registered_compensation"


def test_non_cancelable_work_without_compensation_requires_review():
    result = CancellationPolicy().decide(
        "t4",
        started=True,
        cancelable=False,
        external_side_effect=True,
        compensation_available=False,
        user_revoked=True,
    )
    assert result.action == "human_review"


def test_work_continues_when_no_cancellation_condition_exists():
    result = CancellationPolicy().decide(
        "t5", started=True, cancelable=True, external_side_effect=False, user_revoked=False
    )
    assert result.action == "continue"


def test_task_id_required():
    with pytest.raises(ValueError):
        CancellationPolicy().decide(
            "", started=False, cancelable=True, external_side_effect=False
        )
