"""PI-006 resource-aware provider ranking.

This adapter sits beside the original deterministic router while the scoring
policy is validated. It ranks only providers that are currently usable.
"""

from typing import Iterable, List, Tuple

from .models import Task
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager


class ResourceAwareRouter:
    def __init__(self, providers: Iterable[IntelligenceProvider], resource_manager: ResourceManager):
        self.providers: List[IntelligenceProvider] = list(providers)
        self.resource_manager = resource_manager

        for provider in self.providers:
            snapshot = provider.resource_snapshot()
            self.resource_manager.register_provider(
                provider.name,
                model=provider.model,
                requests_limit=snapshot.requests_limit,
            )

    def select(self, task: Task) -> IntelligenceProvider:
        candidates = [p for p in self.providers if self._available(p)]
        if not candidates:
            raise RuntimeError("No intelligence provider is currently available")

        ranked: List[Tuple[float, IntelligenceProvider]] = [
            (self._score(p, task), p) for p in candidates
        ]
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked[0][1]

    def _available(self, provider: IntelligenceProvider) -> bool:
        snapshot = provider.resource_snapshot()
        return snapshot.available and self.resource_manager.can_request(provider.name)

    def _score(self, provider: IntelligenceProvider, task: Task) -> float:
        snapshot = self.resource_manager.snapshot(provider.name)
        score = 0.0

        # High privacy strongly prefers local execution.
        if task.privacy == "high" and provider.name == "local":
            score += 100.0

        # Explicit local preference is stronger than ordinary quota preference.
        if task.metadata.get("prefer_local") and provider.name == "local":
            score += 50.0

        # Known remaining request capacity is useful, but deliberately capped.
        if snapshot.requests_remaining is not None:
            score += min(float(snapshot.requests_remaining), 25.0)

        # Observed latency matters only when the task requests low latency.
        if task.latency == "low" and snapshot.latency_ms is not None:
            score += max(0.0, 50.0 - min(snapshot.latency_ms, 50.0))

        return score
