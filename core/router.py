"""Resource-aware deterministic provider router for PI-004."""

from typing import Iterable, List

from .models import Task
from .providers import IntelligenceProvider
from .resource_manager import ResourceManager


class IntelligenceRouter:
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
        candidates = [provider for provider in self.providers if self._available(provider)]
        if not candidates:
            raise RuntimeError("No intelligence provider is currently available")

        if task.privacy == "high":
            local = [p for p in candidates if p.name == "local"]
            if local:
                return local[0]

        return candidates[0]

    def _available(self, provider: IntelligenceProvider) -> bool:
        snapshot = provider.resource_snapshot()
        return snapshot.available and self.resource_manager.can_request(provider.name)
