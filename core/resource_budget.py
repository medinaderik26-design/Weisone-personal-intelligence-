"""PI-029 resource budgets for finite AI capacity."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResourceBudget:
    """Optional limits for one unit of work.

    Unknown measurements remain unknown; the budget never estimates them from
    characters, words, or other proxies.
    """

    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    max_total_tokens: Optional[int] = None
    max_cost: Optional[float] = None
    max_latency_ms: Optional[float] = None

    def validate(self) -> None:
        for name in (
            "max_input_tokens",
            "max_output_tokens",
            "max_total_tokens",
        ):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")
        for name in ("max_cost", "max_latency_ms"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True)
class BudgetEvaluation:
    allowed: bool
    reasons: tuple[str, ...] = ()


class ResourceBudgetEvaluator:
    """Evaluate measured resource usage against explicit limits."""

    def evaluate(
        self,
        budget: ResourceBudget,
        *,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        latency_ms: Optional[float] = None,
    ) -> BudgetEvaluation:
        budget.validate()
        reasons = []

        if budget.max_input_tokens is not None and input_tokens is not None:
            if input_tokens > budget.max_input_tokens:
                reasons.append("input token budget exceeded")
        if budget.max_output_tokens is not None and output_tokens is not None:
            if output_tokens > budget.max_output_tokens:
                reasons.append("output token budget exceeded")
        if budget.max_total_tokens is not None and input_tokens is not None and output_tokens is not None:
            if input_tokens + output_tokens > budget.max_total_tokens:
                reasons.append("total token budget exceeded")
        if budget.max_cost is not None and cost is not None and cost > budget.max_cost:
            reasons.append("cost budget exceeded")
        if budget.max_latency_ms is not None and latency_ms is not None and latency_ms > budget.max_latency_ms:
            reasons.append("latency budget exceeded")

        return BudgetEvaluation(allowed=not reasons, reasons=tuple(reasons))
