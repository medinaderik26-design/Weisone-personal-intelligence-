from core.persistent_work_state import WorkState
from core.recovery_coordinator import RecoveryCoordinator


def test_queued_work_resumes_when_provider_available():
    decision = RecoveryCoordinator().decide(WorkState("t1", "queued"))
    assert decision.action == "resume"


def test_queued_work_defers_when_no_provider_exists():
    decision = RecoveryCoordinator().decide(WorkState("t1", "queued"), provider_available=False)
    assert decision.action == "defer"


def test_running_unknown_external_state_requires_review():
    decision = RecoveryCoordinator().decide(WorkState("t1", "running"))
    assert decision.action == "human_review"


def test_running_unknown_state_can_reroute_when_explicitly_available():
    decision = RecoveryCoordinator().decide(
        WorkState("t1", "running"), reroute_available=True
    )
    assert decision.action == "reroute"


def test_failed_retryable_work_retries():
    decision = RecoveryCoordinator().decide(
        WorkState("t1", "failed"), retry_allowed=True
    )
    assert decision.action == "retry"


def test_failed_work_can_reroute():
    decision = RecoveryCoordinator().decide(
        WorkState("t1", "failed"), provider_available=False, retry_allowed=False,
        reroute_available=True
    )
    assert decision.action == "reroute"
