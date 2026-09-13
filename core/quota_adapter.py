"""PI-031 provider quota/reset adapters.

Provider integrations must report quota facts explicitly. This layer does not
infer limits, reset times, or capacity from text, characters, or elapsed time.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol

from .quota_window import QuotaRegistry, QuotaWindow


@dataclass(frozen=True)
class QuotaReport:
    provider: str
    remaining_requests: Optional[int] = None
    limit_requests: Optional[int] = None
    reset_at: Optional[datetime] = None

    def to_window(self) -> QuotaWindow:
        return QuotaWindow(
            provider=self.provider,
            remaining_requests=self.remaining_requests,
            limit_requests=self.limit_requests,
            reset_at=self.reset_at,
        )


class QuotaSource(Protocol):
    def read_quota(self) -> QuotaReport:
        ...


class QuotaAdapter:
    """Normalize a provider-specific quota source into the PI quota registry."""

    def __init__(self, source: QuotaSource, registry: QuotaRegistry) -> None:
        self.source = source
        self.registry = registry

    def refresh(self) -> QuotaWindow:
        report = self.source.read_quota()
        window = report.to_window()
        window.validate()
        self.registry.record(window)
        return window


class StaticQuotaSource:
    """Deterministic source for tests and local development."""

    def __init__(self, report: QuotaReport) -> None:
        self.report = report

    def read_quota(self) -> QuotaReport:
        return self.report
