"""PI-008 task-specific provider performance history."""

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class TaskPerformance:
    provider: str
    task_type: str
    successes: int = 0
    failures: int = 0
    quality_sum: float = 0.0
    quality_samples: int = 0
    latency_sum_ms: float = 0.0
    latency_samples: int = 0

    @property
    def sample_count(self) -> int:
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        return self.successes / self.sample_count if self.sample_count else 0.0

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
class TaskPerformanceRegistry:
    history: Dict[Tuple[str, str], TaskPerformance] = field(default_factory=dict)

    def ensure(self, provider: str, task_type: str) -> TaskPerformance:
        key = (provider, task_type)
        if key not in self.history:
            self.history[key] = TaskPerformance(provider=provider, task_type=task_type)
        return self.history[key]

    def record(
        self,
        provider: str,
        task_type: str,
        *,
        success: bool,
        quality: Optional[float] = None,
        latency_ms: Optional[float] = None,
    ) -> TaskPerformance:
        performance = self.ensure(provider, task_type)
        if success:
            performance.successes += 1
        else:
            performance.failures += 1
        if quality is not None:
            performance.quality_sum += quality
            performance.quality_samples += 1
        if latency_ms is not None:
            performance.latency_sum_ms += latency_ms
            performance.latency_samples += 1
        return performance

    def get(self, provider: str, task_type: str) -> TaskPerformance:
        return self.ensure(provider, task_type)
