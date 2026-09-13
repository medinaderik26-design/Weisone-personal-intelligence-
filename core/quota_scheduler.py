"""PI-032 quota-aware scheduling decisions.

Turns explicit quota/reset facts into scheduler decisions. It never infers a
reset time or treats unknown quota as exhausted.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .quota_window import QuotaRegistry


@dataclass(frozen=True)
class QuotaScheduleDecision:
    provider: str
    action: str
    reason: str
    retry_at: Optional[datetime] = None


class QuotaAwareScheduler:
    def __init__(self, quotas: QuotaRegistry) -> None:
        self.quotas = quotas

    def decide(self, provider: str, *, now: Optional[datetime] = None) -> QuotaScheduleDecision:
        current = now or datetime.now(timezone.utc)
        window = self.quotas.get(provider)

        if window is None or not window.known:
            return QuotaScheduleDecision(
                provider=provider,
                action="eligible",
                reason="quota capacity is unknown; no exhaustion is assumed",
            )

        if not window.exhausted:
            return QuotaScheduleDecision(
                provider=provider,
                action="eligible",
                reason="reported quota capacity remains",
            )

        if window.reset_at is not None and window.reset_at > current:
            return QuotaScheduleDecision(
                provider=provider,
                action="defer",
                reason="reported quota is exhausted until the provider reset",
                retry_at=window.reset_at,
            )

        if window.reset_at is not None and window.reset_at <= current:
            return QuotaScheduleDecision(
                provider=provider,
                action="refresh",
                reason="reported reset time has passed; refresh quota before execution",
            )

        return QuotaScheduleDecision(
            provider=provider,
            action="reroute",
            reason="quota is exhausted and no reset time is known",
        )
