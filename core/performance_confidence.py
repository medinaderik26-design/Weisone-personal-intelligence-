"""PI-009 confidence gates for measured provider performance."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ConfidencePolicy:
    min_samples: int = 3
    min_quality_samples: int = 3
    minimum_success_rate: float = 0.0


@dataclass(frozen=True)
class PerformanceEvidence:
    provider: str
    task_type: str
    sample_count: int
    success_rate: float
    quality_average: Optional[float]
    quality_samples: int

    @property
    def has_enough_samples(self) -> bool:
        return self.sample_count >= 1


class PerformanceConfidence:
    def __init__(self, policy: ConfidencePolicy | None = None) -> None:
        self.policy = policy or ConfidencePolicy()

    def is_reliable(self, evidence: PerformanceEvidence) -> bool:
        if evidence.sample_count < self.policy.min_samples:
            return False
        if evidence.success_rate < self.policy.minimum_success_rate:
            return False
        if evidence.quality_average is not None:
            return evidence.quality_samples >= self.policy.min_quality_samples
        return False

    def score(self, evidence: PerformanceEvidence) -> Optional[float]:
        if not self.is_reliable(evidence):
            return None
        return evidence.quality_average
