"""PI-011 standardized execution telemetry records."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ExecutionTelemetry:
    """A normalized, provider-neutral record of one execution."""

    task_id: str
    task_type: str
    provider: str
    model: str
    success: bool
    latency_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    quality: Optional[float] = None
    quality_source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> None:
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.task_type:
            raise ValueError("task_type is required")
        if not self.provider:
            raise ValueError("provider is required")
        if not self.model:
            raise ValueError("model is required")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative")
        if self.input_tokens is not None and self.input_tokens < 0:
            raise ValueError("input_tokens cannot be negative")
        if self.output_tokens is not None and self.output_tokens < 0:
            raise ValueError("output_tokens cannot be negative")
        if self.estimated_cost is not None and self.estimated_cost < 0:
            raise ValueError("estimated_cost cannot be negative")
        if self.quality is not None and not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0.0 and 1.0")
        if self.quality is not None and not self.quality_source:
            raise ValueError("quality_source is required when quality is supplied")
