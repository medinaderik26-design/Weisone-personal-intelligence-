"""PI-007 provider health and measured quality history."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ProviderHealth:
    provider: str
    successes: int = 0
    failures: int = 0
    quality_sum: float = 0.0
    quality_samples: int = 0
    latency_sum_ms: float = 0.0
    latency_samples: int = 0

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total else 0.0

    @property
    def quality_average(self) -> Optional[float]:
        if not self.quality_samples:
            return None
        return self.quality_sum / self.quality_samples

    @property
    def latency_average_ms(self) -> Optional[float]:
        if not self.latency_samples:
            return None
        return self.latency_sum_ms / self.latency_samples


@dataclass
class ProviderHealthRegistry:
    providers: Dict[str, ProviderHealth] = field(default_factory=dict)

    def ensure(self, provider: str) -> ProviderHealth:
        if provider not in self.providers:
            self.providers[provider] = ProviderHealth(provider=provider)
        return self.providers[provider]

    def record(
        self,
        provider: str,
        *,
        success: bool,
        quality: Optional[float] = None,
        latency_ms: Optional[float] = None,
    ) -> ProviderHealth:
        health = self.ensure(provider)
        if success:
            health.successes += 1
        else:
            health.failures += 1
        if quality is not None:
            health.quality_sum += quality
            health.quality_samples += 1
        if latency_ms is not None:
            health.latency_sum_ms += latency_ms
            health.latency_samples += 1
        return health

    def get(self, provider: str) -> ProviderHealth:
        return self.ensure(provider)
