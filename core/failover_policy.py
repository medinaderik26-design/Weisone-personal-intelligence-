"""PI-033 local-first fallback and provider failover policy."""

from dataclasses import dataclass
from typing import Iterable, List

from .models import Task
from .providers import IntelligenceProvider


@dataclass(frozen=True)
class FailoverDecision:
    provider: str
    action: str
    reason: str


class FailoverPolicy:
    """Choose a safe fallback without executing the task.

    High-privacy work is local-only. Other work may fall back to local when
    explicitly allowed by task metadata. Failover never bypasses permissions.
    """

    def decide(
        self,
        task: Task,
        providers: Iterable[IntelligenceProvider],
        excluded: Iterable[str] = (),
    ) -> FailoverDecision:
        excluded_set = set(excluded)
        candidates: List[IntelligenceProvider] = [
            provider
            for provider in providers
            if provider.name not in excluded_set and provider.resource_snapshot().available
        ]

        if task.privacy == "high":
            local = [p for p in candidates if p.name == "local"]
            if local:
                return FailoverDecision("local", "failover", "high-privacy task requires local execution")
            return FailoverDecision("", "human_review", "no authorized local provider is available")

        if task.metadata.get("allow_local_fallback", True):
            local = [p for p in candidates if p.name == "local"]
            if local:
                return FailoverDecision("local", "failover", "local fallback is permitted")

        if candidates:
            return FailoverDecision(candidates[0].name, "reroute", "alternate eligible provider is available")

        return FailoverDecision("", "defer", "no eligible fallback provider is available")
