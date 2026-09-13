"""PI-016 fusion of measured performance and resource signals."""

from dataclasses import dataclass
from typing import Iterable, List

from .models import Task
from .performance_confidence import PerformanceConfidence, PerformanceEvidence
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager
from .task_performance import TaskPerformanceRegistry


@dataclass(frozen=True)
class FusionWeights:
    """Weights for measured signals after hard constraints are applied."""

    quality: float = 100.0
    success_rate: float = 10.0
    latency: float = 1.0
    remaining_requests: float = 0.05


class PerformanceResourceFusionRouter:
    """Choose providers using measured task performance plus resource state."""

    def __init__(
        self,
        providers: Iterable[IntelligenceProvider],
        resource_manager: ResourceManager,
        performance: TaskPerformanceRegistry,
        confidence: PerformanceConfidence | None = None,
        weights: FusionWeights | None = None,
    ) -> None:
        self.providers: List[IntelligenceProvider] = list(providers)
        self.resource_manager = resource_manager
        self.performance = performance
        self.confidence = confidence or PerformanceConfidence()
        self.weights = weights or FusionWeights()

    def select(self, task: Task) -> IntelligenceProvider:
        candidates = [p for p in self.providers if self._eligible(task, p)]
        if not candidates:
            raise RuntimeError("No intelligence provider is currently available")

        if task.privacy == "high":
            local = [p for p in candidates if p.name == "local"]
            if local:
                candidates = local

        return max(candidates, key=lambda provider: self.score(provider, task))

    def score(self, provider: IntelligenceProvider, task: Task) -> float:
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

        score = 0.0
        if confidence_score is not None:
            score += self.weights.quality * confidence_score
            score += self.weights.success_rate * evidence.success_rate

        if task.metadata.get("low_latency") and evidence.latency_average_ms is not None:
            score += self.weights.latency / max(evidence.latency_average_ms, 1.0)

        snapshot = provider.resource_snapshot()
        remaining = snapshot.requests_remaining
        if remaining is not None:
            score += self.weights.remaining_requests * remaining

        return score

    def _eligible(self, task: Task, provider: IntelligenceProvider) -> bool:
        snapshot = provider.resource_snapshot()
        if not snapshot.available:
            return False
        if not self.resource_manager.can_request(provider.name):
            return False
        return task.privacy != "high" or provider.name == "local"

    @staticmethod
    def _task_type(task: Task) -> str:
        return str(task.metadata.get("task_type", task.task_type))
