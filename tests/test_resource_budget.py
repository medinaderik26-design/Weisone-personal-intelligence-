import pytest

from core.resource_budget import ResourceBudget, ResourceBudgetEvaluator


def test_budget_allows_usage_within_limits():
    result = ResourceBudgetEvaluator().evaluate(
        ResourceBudget(max_input_tokens=100, max_output_tokens=50, max_total_tokens=120),
        input_tokens=80,
        output_tokens=30,
    )
    assert result.allowed is True
    assert result.reasons == ()


def test_budget_rejects_excess_input_tokens():
    result = ResourceBudgetEvaluator().evaluate(
        ResourceBudget(max_input_tokens=100), input_tokens=101
    )
    assert result.allowed is False
    assert "input token budget exceeded" in result.reasons


def test_budget_rejects_excess_total_tokens():
    result = ResourceBudgetEvaluator().evaluate(
        ResourceBudget(max_total_tokens=120), input_tokens=80, output_tokens=41
    )
    assert result.allowed is False


def test_unknown_usage_is_not_invented():
    result = ResourceBudgetEvaluator().evaluate(
        ResourceBudget(max_input_tokens=100, max_cost=1.0),
        input_tokens=None,
        cost=None,
    )
    assert result.allowed is True


def test_negative_budget_rejected():
    with pytest.raises(ValueError):
        ResourceBudget(max_cost=-1).validate()
