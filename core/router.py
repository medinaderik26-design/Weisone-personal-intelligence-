"""Deterministic provider router for PI-001."""

from typing import Iterable, List
from .models import ResourceSnapshot, Task
from .providers import IntelligenceProvider


class IntelligenceRouter:
    def __init__(self, providers: Iterable[IntelligenceProvider]):
        self.providers: List[IntelligenceProvider] = list(providers)

    def select(self, task: Task) -> IntelligenceProvider:
        candidates = [
            provider
            for provider in self.providers
            if provider.resource_snapshot().available
        ]
        if not candidates:
            raise RuntimeError("No intelligence provider is currently available")

        # PI-001 intentionally uses deterministic selection. Ranking by capability,
        # privacy, quota, latency, and measured quality comes in the next iteration.
        if task.privacy == "high":
            local = [p for p in candidates if p.name == "local"]
            if local:
                return local[0]
        return candidates[0]
