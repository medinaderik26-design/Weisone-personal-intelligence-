"""PI-015 deterministic resource-aware decision policy."""

from dataclasses import dataclass
from typing import Optional

from .models import Task
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager


@dataclass(frozen=True)
class ResourcePolicy:
    """Policy weights for optional resource signals.

    Hard constraints are handled separately from these preferences.
    """

    cost_weight: float = 1.0
    latency_weight: float = 1.0
    remaining_requests_weight: float = 0.25


class ResourceAwareDecisionPolicy:
    """Rank eligible providers using measured resource information only."""

    def __init__(self, resource_manager: ResourceManager, policy: Optional[ResourcePolicy] = None) -> None:
        self.resource_manager = resource_manager
        self.policy = policy or ResourcePolicy()

    def rank(self, task: Task, providers: list[IntelligenceProvider]) -> list[IntelligenceProvider]:
        eligible = [provider for provider in providers if self._eligible(task, provider)]
        return sorted(eligible, key=lambda provider: self._score(task, provider), reverse=True)

    def _eligible(self, task: Task, provider: IntelligenceProvider) -> bool:
        snapshot = provider.resource_snapshot()
        if not snapshot.available:
            return False
        if not self.resource_manager.can_request(provider.name):
            return False
        if task.privacy == "high" and provider.name != "local":
            return False
        return True

    def _score(self, task: Task, provider: IntelligenceProvider) -> float:
        snapshot = provider.resource_snapshot()
        score = 0.0

        # Prefer lower measured latency only when the task asks for it.
        if task.metadata.get("low_latency"):
            latency = snapshot.latency_ms
            if latency is not None:
                score += self.policy.latency_weight / max(latency, 1.0)

        # Prefer providers with more remaining request capacity.
        if snapshot.requests_limit is not None:
            remaining = max(snapshot.requests_limit - snapshot.requests_used, 0)
            score += self.policy.remaining_requests_weight * remaining

        return score
