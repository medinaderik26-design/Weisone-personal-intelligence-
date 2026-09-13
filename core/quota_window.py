"""Quota-window state for provider capacity planning.

This module models only quota facts explicitly reported by a provider.
It does not estimate reset times or convert character counts into tokens.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class QuotaWindow:
    provider: str
    remaining_requests: Optional[int] = None
    limit_requests: Optional[int] = None
    reset_at: Optional[datetime] = None

    def validate(self) -> None:
        if not self.provider:
            raise ValueError("provider is required")
        if self.remaining_requests is not None and self.remaining_requests < 0:
            raise ValueError("remaining_requests cannot be negative")
        if self.limit_requests is not None and self.limit_requests < 0:
            raise ValueError("limit_requests cannot be negative")
        if (
            self.remaining_requests is not None
            and self.limit_requests is not None
            and self.remaining_requests > self.limit_requests
        ):
            raise ValueError("remaining_requests cannot exceed limit_requests")

    @property
    def exhausted(self) -> bool:
        return self.remaining_requests == 0

    @property
    def known(self) -> bool:
        return self.remaining_requests is not None


class QuotaRegistry:
    """Stores the latest explicitly reported quota window per provider."""

    def __init__(self) -> None:
        self._windows: dict[str, QuotaWindow] = {}

    def record(self, window: QuotaWindow) -> None:
        window.validate()
        self._windows[window.provider] = window

    def get(self, provider: str) -> Optional[QuotaWindow]:
        return self._windows.get(provider)

    def can_execute(self, provider: str) -> bool:
        window = self.get(provider)
        return window is None or not window.exhausted
