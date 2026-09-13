"""PI-013 resource outcome accounting."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ResourceOutcome:
    """Measured resource usage for one execution."""

    provider: str
    task_id: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    cost: Optional[float] = None

    def validate(self) -> None:
        if not self.provider:
            raise ValueError("provider is required")
        if not self.task_id:
            raise ValueError("task_id is required")
        if self.input_tokens is not None and self.input_tokens < 0:
            raise ValueError("input_tokens cannot be negative")
        if self.output_tokens is not None and self.output_tokens < 0:
            raise ValueError("output_tokens cannot be negative")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")
        if self.cost is not None and self.cost < 0:
            raise ValueError("cost cannot be negative")


@dataclass
class ResourceOutcomeRegistry:
    outcomes: list[ResourceOutcome]

    def __init__(self) -> None:
        self.outcomes = []

    def record(self, outcome: ResourceOutcome) -> ResourceOutcome:
        outcome.validate()
        self.outcomes.append(outcome)
        return outcome

    def for_provider(self, provider: str) -> list[ResourceOutcome]:
        return [item for item in self.outcomes if item.provider == provider]

    def total_cost(self, provider: Optional[str] = None) -> Optional[float]:
        values = self.outcomes if provider is None else self.for_provider(provider)
        costs = [item.cost for item in values if item.cost is not None]
        return sum(costs) if costs else None

    def total_tokens(self, provider: Optional[str] = None) -> Optional[int]:
        values = self.outcomes if provider is None else self.for_provider(provider)
        known = [item for item in values if item.input_tokens is not None and item.output_tokens is not None]
        if not known:
            return None
        return sum(item.input_tokens + item.output_tokens for item in known)
