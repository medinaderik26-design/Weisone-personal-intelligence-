"""PI-009 routing that refuses to over-trust sparse evidence."""

from typing import Iterable, List

from .models import Task
from .performance_confidence import PerformanceConfidence, PerformanceEvidence
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager
from .task_performance import TaskPerformanceRegistry


class ConfidenceAwareRouter:
    """Use task-specific quality only after the evidence crosses a confidence gate."""

    def __init__(
        self,
        providers: Iterable[IntelligenceProvider],
        resource_manager: ResourceManager,
        performance: TaskPerformanceRegistry,
        confidence: PerformanceConfidence | None = None,
    ) -> None:
        self.providers: List[IntelligenceProvider] = list(providers)
        self.resource_manager = resource_manager
        self.performance = performance
        self.confidence = confidence or PerformanceConfidence()

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
        confidence_score = self.confidence.score(
            PerformanceEvidence(
                provider=provider.name,
                task_type=self._task_type(task),
                sample_count=evidence.sample_count,
                success_rate=evidence.success_rate,
                quality_average=evidence.quality_average,
                quality_samples=evidence.quality_samples,
            )
        )

        # No confidence means no quality bonus. Fall back to neutral routing.
        score = 0.0 if confidence_score is None else confidence_score * 100.0

        if task.metadata.get("low_latency") and evidence.latency_average_ms is not None:
            score += 1000.0 / max(evidence.latency_average_ms, 1.0)

        return score

    @staticmethod
    def _task_type(task: Task) -> str:
        return str(task.metadata.get("task_type", "general"))
