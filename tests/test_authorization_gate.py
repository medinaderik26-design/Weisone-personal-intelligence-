from core.authorization_gate import PreExecutionAuthorizationGate
from core.data_boundary import DataBoundary, DataField
from core.provider_policy import ProviderPolicy, ProviderPolicyRegistry
from core.resource_budget import ResourceBudget, ResourceBudgetEvaluator
from core.models import Task


def gate_with(*policies):
    registry = ProviderPolicyRegistry()
    for policy in policies:
        registry.register(policy)
    return PreExecutionAuthorizationGate(registry, DataBoundary(), ResourceBudgetEvaluator())


def test_unknown_provider_is_denied():
    gate = gate_with()
    result = gate.authorize(Task("t1", "hello"), provider="cloud")
    assert result.allowed is False


def test_authorized_task_passes_final_gate():
    gate = gate_with(
        ProviderPolicy(provider="cloud", allowed_sensitivities=frozenset({"normal"}))
    )
    result = gate.authorize(
        Task("t2", "summarize", task_type="summary"),
        provider="cloud",
        fields=[DataField("document", "normal", "summary")],
        budget=ResourceBudget(max_input_tokens=100),
        input_tokens=20,
    )
    assert result.allowed is True
    assert result.fields == ("document",)


def test_high_privacy_requires_policy_and_local_boundary():
    gate = gate_with(
        ProviderPolicy(provider="cloud", allowed_sensitivities=frozenset({"sensitive"}), allow_high_privacy=True)
    )
    result = gate.authorize(
        Task("t3", "private", privacy="high"),
        provider="cloud",
        fields=[DataField("note", "sensitive")],
        authorized_sensitivities={"sensitive"},
    )
    assert result.allowed is False


def test_external_side_effect_requires_provider_authorization():
    gate = gate_with(ProviderPolicy(provider="cloud"))
    result = gate.authorize(
        Task("t4", "send", metadata={"external_side_effect": True}),
        provider="cloud",
    )
    assert result.allowed is False


def test_budget_failure_blocks_execution():
    gate = gate_with(ProviderPolicy(provider="cloud"))
    result = gate.authorize(
        Task("t5", "work"),
        provider="cloud",
        budget=ResourceBudget(max_input_tokens=10),
        input_tokens=11,
    )
    assert result.allowed is False
    assert "input token budget exceeded" in result.reasons
