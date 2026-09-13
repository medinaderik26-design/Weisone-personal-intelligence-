"""Resource accounting primitives for Weisone Personal Intelligence.

v0.1 intentionally tracks logical request budgets. Provider-specific quota
and billing integrations will be added through adapters later.
"""

from dataclasses import dataclass, field
from time import monotonic
from typing import Dict, Optional


@dataclass
class ResourceSnapshot:
    provider: str
    requests_used: int = 0
    requests_limit: Optional[int] = None
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    failures: int = 0

    @property
    def requests_remaining(self) -> Optional[int]:
        if self.requests_limit is None:
            return None
        return max(self.requests_limit - self.requests_used, 0)


@dataclass
class ResourceManager:
    snapshots: Dict[str, ResourceSnapshot] = field(default_factory=dict)

    def register_provider(
        self,
        provider: str,
        *,
        requests_limit: Optional[int] = None,
    ) -> ResourceSnapshot:
        snapshot = self.snapshots.get(provider)
        if snapshot is None:
            snapshot = ResourceSnapshot(
                provider=provider,
                requests_limit=requests_limit,
            )
            self.snapshots[provider] = snapshot
        elif requests_limit is not None:
            snapshot.requests_limit = requests_limit
        return snapshot

    def can_request(self, provider: str) -> bool:
        snapshot = self.snapshots.get(provider)
        if snapshot is None:
            return False
        remaining = snapshot.requests_remaining
        return remaining is None or remaining > 0

    def record_request(
        self,
        provider: str,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost: float = 0.0,
        failed: bool = False,
    ) -> ResourceSnapshot:
        snapshot = self.snapshots[provider]
        snapshot.requests_used += 1
        snapshot.input_tokens += input_tokens
        snapshot.output_tokens += output_tokens
        snapshot.estimated_cost += estimated_cost
        if failed:
            snapshot.failures += 1
        return snapshot

    def snapshot(self, provider: str) -> ResourceSnapshot:
        return self.snapshots[provider]

    def all_snapshots(self) -> Dict[str, ResourceSnapshot]:
        return dict(self.snapshots)
