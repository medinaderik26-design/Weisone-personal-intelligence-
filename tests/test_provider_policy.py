from core.models import Task
from core.provider_policy import ProviderPolicy, ProviderPolicyRegistry


def test_provider_policy_allows_only_declared_sensitivity():
    policy = ProviderPolicy(provider="cloud", allowed_sensitivities=frozenset({"normal"}))
    assert policy.permits(Task("t1", "x"), "normal") is True
    assert policy.permits(Task("t2", "x"), "sensitive") is False


def test_high_privacy_requires_explicit_provider_permission():
    task = Task("t3", "x", privacy="high")
    denied = ProviderPolicy(provider="cloud", allowed_sensitivities=frozenset({"sensitive"}))
    allowed = ProviderPolicy(
        provider="local",
        allowed_sensitivities=frozenset({"sensitive"}),
        allow_high_privacy=True,
    )
    assert denied.permits(task, "sensitive") is False
    assert allowed.permits(task, "sensitive") is True


def test_external_side_effects_are_denied_by_default():
    task = Task("t4", "send email", metadata={"external_side_effect": True})
    policy = ProviderPolicy(provider="cloud", allowed_sensitivities=frozenset({"normal"}))
    assert policy.permits(task) is False


def test_registry_requires_registered_policy():
    registry = ProviderPolicyRegistry()
    task = Task("t5", "x")
    assert registry.permits("cloud", task) is False
    registry.register(ProviderPolicy(provider="cloud"))
    assert registry.permits("cloud", task) is True
