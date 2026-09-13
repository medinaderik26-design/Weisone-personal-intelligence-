"""Resource accounting primitives for Weisone Personal Intelligence.

v0.1 intentionally tracks logical request budgets. Provider-specific quota
and billing integrations will be added through adapters later.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from .models import ResourceSnapshot


@dataclass
class ResourceManager:
    snapshots: Dict[str, ResourceSnapshot] = field(default_factory=dict)

    def register_provider(
        self,
        provider: str,
        *,
        model: str = "unknown",
        requests_limit: Optional[int] = None,
    ) -> ResourceSnapshot:
        snapshot = self.snapshots.get(provider)
        if snapshot is None:
            snapshot = ResourceSnapshot(
                provider=provider,
                model=model,
                requests_limit=requests_limit,
            )
            self.snapshots[provider] = snapshot
        else:
            if model != "unknown":
                snapshot.model = model
            if requests_limit is not None:
                snapshot.requests_limit = requests_limit
        return snapshot

    def can_request(self, provider: str) -> bool:
        snapshot = self.snapshots.get(provider)
        if snapshot is None or not snapshot.available:
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
        latency_ms: Optional[float] = None,
        failed: bool = False,
    ) -> ResourceSnapshot:
        snapshot = self.snapshots[provider]
        snapshot.requests_used += 1
        snapshot.input_tokens += input_tokens
        snapshot.output_tokens += output_tokens
        snapshot.estimated_cost += estimated_cost
        if latency_ms is not None:
            snapshot.latency_ms = latency_ms
        if failed:
            snapshot.failures += 1
        return snapshot

    def snapshot(self, provider: str) -> ResourceSnapshot:
        return self.snapshots[provider]

    def all_snapshots(self) -> Dict[str, ResourceSnapshot]:
        return dict(self.snapshots)
