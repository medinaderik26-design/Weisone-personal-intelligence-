from core.failover_policy import FailoverPolicy
from core.models import Task
from core.providers import EchoProvider, SimulatedCloudProvider


def test_high_privacy_fails_over_to_local():
    task = Task(task_id="t1", prompt="private", privacy="high")
    result = FailoverPolicy().decide(
        task,
        [SimulatedCloudProvider(available=True), EchoProvider()],
        excluded={"cloud-sim"},
    )
    assert result.provider == "local"
    assert result.action == "failover"


def test_local_fallback_can_be_disabled():
    task = Task(
        task_id="t2",
        prompt="normal",
        metadata={"allow_local_fallback": False},
    )
    result = FailoverPolicy().decide(task, [EchoProvider()], excluded={"local"})
    assert result.action == "defer"


def test_alternate_provider_can_be_selected():
    task = Task(task_id="t3", prompt="normal", metadata={"allow_local_fallback": False})
    result = FailoverPolicy().decide(
        task,
        [SimulatedCloudProvider(available=True)],
        excluded={"primary"},
    )
    assert result.provider == "cloud-sim"
    assert result.action == "reroute"


def test_missing_local_for_high_privacy_requires_review():
    task = Task(task_id="t4", prompt="private", privacy="high")
    result = FailoverPolicy().decide(task, [SimulatedCloudProvider(available=True)])
    assert result.action == "human_review"
