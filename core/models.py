"""Core data contracts for Personal Intelligence v0.1.

These contracts intentionally avoid provider-specific and memory-implementation-specific
assumptions. They are the stable boundary between the intelligence layer and its adapters.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Identity:
    person_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)


@dataclass
class Permission:
    resource: str
    action: str
    allowed: bool = False


@dataclass
class Task:
    task_id: str
    prompt: str
    task_type: str = "general"
    privacy: str = "normal"
    context_required: str = "normal"
    latency: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    provider: str
    model: str = "unknown"
    available: bool = True
    remaining_quota: Optional[float] = None
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: Optional[float] = None
    requests_used: int = 0
    requests_limit: Optional[int] = None
    failures: int = 0

    @property
    def requests_remaining(self) -> Optional[int]:
        if self.requests_limit is None:
            return None
        return max(self.requests_limit - self.requests_used, 0)


@dataclass
class Result:
    task_id: str
    provider: str
    model: str
    text: str
    success: bool = True
    latency_ms: Optional[float] = None
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContinuityEvent:
    task_id: str
    kind: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    task: Task
    result: Result
    continuity_updated: bool
