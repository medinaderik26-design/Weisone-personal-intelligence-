"""PI-008 router scoring from measured task-specific performance."""

from typing import Iterable, List

from .models import Task
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager
from .task_performance import TaskPerformanceRegistry


class PerformanceAwareRouter:
    """Prefer measured task performance while preserving hard constraints."""

    def __init__(
        self,
        providers: Iterable[IntelligenceProvider],
        resource_manager: ResourceManager,
        performance: TaskPerformanceRegistry,
    ) -> None:
        self.providers: List[IntelligenceProvider] = list(providers)
        self.resource_manager = resource_manager
        self.performance = performance

    def select(self, task: Task) -> IntelligenceProvider:
        candidates = [p for p in self.providers if self._available(p)]
        if not candidates:
            raise RuntimeError("No intelligence provider is currently available")

        if task.privacy == "high":
            local = [p for p in candidates if p.name == "local"]
            if local:
                candidates = local

        scored = [(self._score(provider, task), provider) for provider in candidates]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def _available(self, provider: IntelligenceProvider) -> bool:
        snapshot = provider.resource_snapshot()
        return snapshot.available and self.resource_manager.can_request(provider.name)

    def _score(self, provider: IntelligenceProvider, task: Task) -> float:
        evidence = self.performance.get(provider.name, self._task_type(task))
        score = 0.0

        # Measured quality is the strongest signal when it exists.
        if evidence.quality_average is not None:
            score += evidence.quality_average * 100.0

        # Observed success is useful but cannot replace quality evaluation.
        if evidence.sample_count:
            score += evidence.success_rate * 10.0

        # Only use latency when the task explicitly asks for low latency.
        if task.metadata.get("low_latency") and evidence.latency_average_ms is not None:
            score += 1000.0 / max(evidence.latency_average_ms, 1.0)

        # Unknown performance receives no bonus; it is not treated as failure.
        return score

    @staticmethod
    def _task_type(task: Task) -> str:
        return str(task.metadata.get("task_type", "general"))
