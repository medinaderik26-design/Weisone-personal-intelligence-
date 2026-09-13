"""PI-035 provider-specific data and action policies."""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

from .models import Task


@dataclass(frozen=True)
class ProviderPolicy:
    provider: str
    allowed_sensitivities: FrozenSet[str] = frozenset({"normal"})
    allowed_task_types: FrozenSet[str] = frozenset()
    allow_high_privacy: bool = False
    allow_external_side_effects: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

    def permits(self, task: Task, sensitivity: str = "normal") -> bool:
        if sensitivity not in self.allowed_sensitivities:
            return False
        if self.allowed_task_types and task.task_type not in self.allowed_task_types:
            return False
        if task.privacy == "high" and not self.allow_high_privacy:
            return False
        if task.metadata.get("external_side_effect", False) and not self.allow_external_side_effects:
            return False
        return True


class ProviderPolicyRegistry:
    def __init__(self) -> None:
        self._policies: Dict[str, ProviderPolicy] = {}

    def register(self, policy: ProviderPolicy) -> None:
        if not policy.provider:
            raise ValueError("provider is required")
        self._policies[policy.provider] = policy

    def get(self, provider: str) -> ProviderPolicy | None:
        return self._policies.get(provider)

    def permits(self, provider: str, task: Task, sensitivity: str = "normal") -> bool:
        policy = self.get(provider)
        return policy is not None and policy.permits(task, sensitivity)
