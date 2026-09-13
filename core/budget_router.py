"""PI-030 quota and resource-budget routing.

This layer decides where a task may run before execution. It combines hard
eligibility constraints with explicitly measured preflight facts. Unknown
usage stays unknown; the router never invents token counts or costs.
"""

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .models import Task
from .performance_confidence import PerformanceConfidence, PerformanceEvidence
from .providers import IntelligenceProvider
from .quota_window import QuotaRegistry
from .resource_budget import ResourceBudget, ResourceBudgetEvaluator
from .resource_manager import ResourceManager
from .task_performance import TaskPerformanceRegistry


@dataclass(frozen=True)
class BudgetRoutingDecision:
    provider: str
    allowed: bool
    reasons: tuple[str, ...] = ()
    input_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None


class BudgetAwareRouter:
    """Select an eligible provider while enforcing known preflight limits."""

    def __init__(
        self,
        providers: Iterable[IntelligenceProvider],
        resource_manager: ResourceManager,
        quota_registry: QuotaRegistry,
        performance: TaskPerformanceRegistry,
        confidence: PerformanceConfidence,
    ) -> None:
        self.providers: List[IntelligenceProvider] = list(providers)
        self.resource_manager = resource_manager
        self.quota_registry = quota_registry
        self.performance = performance
        self.confidence = confidence
        self.budget_evaluator = ResourceBudgetEvaluator()

    def select(self, task: Task, budget: Optional[ResourceBudget] = None) -> BudgetRoutingDecision:
        candidates: List[tuple[IntelligenceProvider, float]] = []
        rejected: List[str] = []

        preflight_input = self._known_int(task, "input_tokens")
        preflight_cost = self._known_float(task, "estimated_cost")

        for provider in self.providers:
            name = provider.name
            snapshot = provider.resource_snapshot()

            if not snapshot.available:
                rejected.append(f"{name}: unavailable")
                continue
            if not self.resource_manager.can_request(name):
                rejected.append(f"{name}: resource capacity unavailable")
                continue
            if not self.quota_registry.can_execute(name):
                rejected.append(f"{name}: quota exhausted")
                continue
            if task.privacy == "high" and name != "local":
                rejected.append(f"{name}: high-privacy task requires local provider")
                continue

            if budget is not None:
                evaluation = self.budget_evaluator.evaluate(
                    budget,
                    input_tokens=preflight_input,
                    cost=preflight_cost,
                    latency_ms=snapshot.latency_ms,
                )
                if not evaluation.allowed:
                    rejected.extend(f"{name}: {reason}" for reason in evaluation.reasons)
                    continue

            score = self._score(provider, task)
            candidates.append((provider, score))

        if not candidates:
            reason = "; ".join(rejected) or "no eligible provider"
            return BudgetRoutingDecision(
                provider="",
                allowed=False,
                reasons=(reason,),
                input_tokens=preflight_input,
                estimated_cost=preflight_cost,
            )

        provider, _ = max(candidates, key=lambda item: item[1])
        return BudgetRoutingDecision(
            provider=provider.name,
            allowed=True,
            reasons=(),
            input_tokens=preflight_input,
            estimated_cost=preflight_cost,
        )

    def _score(self, provider: IntelligenceProvider, task: Task) -> float:
        performance = self.performance.get(provider.name, task.task_type)
        evidence = PerformanceEvidence(
            provider=provider.name,
            task_type=task.task_type,
            sample_count=performance.sample_count,
            success_rate=performance.success_rate,
            quality_average=performance.quality_average,
            quality_samples=performance.quality_samples,
        )
        quality = self.confidence.score(evidence)
        score = quality if quality is not None else 0.0

        if task.latency == "low" and performance.latency_average_ms is not None:
            score += 1.0 / max(performance.latency_average_ms, 1.0)

        quota = self.quota_registry.get(provider.name)
        if quota is not None and quota.remaining_requests is not None:
            score += min(quota.remaining_requests, 1000) / 1000.0

        return score

    @staticmethod
    def _known_int(task: Task, key: str) -> Optional[int]:
        value = task.metadata.get(key)
        return value if isinstance(value, int) and value >= 0 else None

    @staticmethod
    def _known_float(task: Task, key: str) -> Optional[float]:
        value = task.metadata.get(key)
        return value if isinstance(value, (int, float)) and value >= 0 else None
