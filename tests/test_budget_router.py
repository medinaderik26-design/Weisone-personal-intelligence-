import pytest

from core.budget_router import BudgetAwareRouter
from core.models import Task
from core.performance_confidence import PerformanceConfidence
from core.providers import EchoProvider, SimulatedCloudProvider
from core.quota_window import QuotaRegistry, QuotaWindow
from core.resource_budget import ResourceBudget
from core.resource_manager import ResourceManager
from core.task_performance import TaskPerformanceRegistry


def build_router():
    providers = [EchoProvider(), SimulatedCloudProvider()]
    resources = ResourceManager()
    resources.register_provider("local", model="echo-v0.1")
    resources.register_provider("cloud-sim", model="cloud-sim-v0.1")
    return BudgetAwareRouter(
        providers,
        resources,
        QuotaRegistry(),
        TaskPerformanceRegistry(),
        PerformanceConfidence(),
    )


def test_budget_router_selects_an_eligible_provider():
    decision = build_router().select(
        Task("t1", "hello", task_type="general"),
        ResourceBudget(max_input_tokens=100),
    )
    assert decision.allowed is True
    assert decision.provider in {"local", "cloud-sim"}


def test_known_input_tokens_can_block_a_provider():
    router = build_router()
    task = Task("t2", "hello", metadata={"input_tokens": 101})
    decision = router.select(task, ResourceBudget(max_input_tokens=100))
    assert decision.allowed is False
    assert "budget exceeded" in decision.reasons[0]


def test_unknown_preflight_usage_is_not_invented():
    decision = build_router().select(
        Task("t3", "hello"),
        ResourceBudget(max_input_tokens=1, max_cost=0.01),
    )
    assert decision.allowed is True


def test_exhausted_quota_is_hard_constraint():
    router = build_router()
    router.quota_registry.record(
        QuotaWindow(provider="local", remaining_requests=0, limit_requests=10)
    )
    decision = router.select(Task("t4", "hello"))
    assert decision.allowed is True
    assert decision.provider == "cloud-sim"


def test_high_privacy_requires_local():
    decision = build_router().select(Task("t5", "private", privacy="high"))
    assert decision.allowed is True
    assert decision.provider == "local"


def test_all_providers_rejected_returns_explicit_failure():
    router = build_router()
    router.quota_registry.record(
        QuotaWindow(provider="local", remaining_requests=0, limit_requests=10)
    )
    router.quota_registry.record(
        QuotaWindow(provider="cloud-sim", remaining_requests=0, limit_requests=10)
    )
    decision = router.select(Task("t6", "hello"))
    assert decision.allowed is False
    assert decision.provider == ""
    assert decision.reasons
