"""PI-036 pre-execution authorization gate."""

from dataclasses import dataclass
from typing import Iterable, Optional

from .data_boundary import DataBoundary, DataField
from .models import Task
from .provider_policy import ProviderPolicyRegistry
from .resource_budget import ResourceBudget, ResourceBudgetEvaluator


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    provider: str
    reasons: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()


class PreExecutionAuthorizationGate:
    """Final policy checkpoint before provider execution."""

    def __init__(
        self,
        policies: ProviderPolicyRegistry,
        data_boundary: DataBoundary,
        budget_evaluator: ResourceBudgetEvaluator,
    ) -> None:
        self.policies = policies
        self.data_boundary = data_boundary
        self.budget_evaluator = budget_evaluator

    def authorize(
        self,
        task: Task,
        *,
        provider: str,
        fields: Iterable[DataField] = (),
        authorized_sensitivities: Iterable[str] = ("normal",),
        budget: Optional[ResourceBudget] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        latency_ms: Optional[float] = None,
    ) -> AuthorizationDecision:
        reasons = []
        policy = self.policies.get(provider)
        if policy is None:
            return AuthorizationDecision(False, provider, ("provider has no registered policy",))

        sensitivity = "normal"
        if fields:
            sensitivity = max(
                (field.sensitivity for field in fields),
                key=lambda value: {"normal": 0, "sensitive": 1, "secret": 2}.get(value, 3),
            )

        if not policy.permits(task, sensitivity):
            reasons.append("provider policy denied the task")

        boundary = self.data_boundary.filter(
            task,
            fields,
            provider=provider,
            authorized_sensitivities=authorized_sensitivities,
        )
        if not boundary.allowed:
            reasons.append(boundary.reason)

        if budget is not None:
            evaluation = self.budget_evaluator.evaluate(
                budget,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency_ms=latency_ms,
            )
            reasons.extend(evaluation.reasons)

        return AuthorizationDecision(
            allowed=not reasons,
            provider=provider,
            reasons=tuple(reasons),
            fields=boundary.fields,
        )
