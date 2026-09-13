from datetime import datetime, timedelta, timezone

from core.quota_scheduler import QuotaAwareScheduler
from core.quota_window import QuotaRegistry, QuotaWindow


def test_available_quota_is_eligible():
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud", remaining_requests=4, limit_requests=10))

    result = QuotaAwareScheduler(registry).decide("cloud")

    assert result.action == "eligible"


def test_exhausted_quota_with_future_reset_is_deferred():
    now = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
    reset = now + timedelta(hours=2)
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud", remaining_requests=0, limit_requests=10, reset_at=reset))

    result = QuotaAwareScheduler(registry).decide("cloud", now=now)

    assert result.action == "defer"
    assert result.retry_at == reset


def test_exhausted_quota_without_reset_reroutes():
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud", remaining_requests=0, limit_requests=10))

    result = QuotaAwareScheduler(registry).decide("cloud")

    assert result.action == "reroute"


def test_passed_reset_requires_refresh():
    now = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
    reset = now - timedelta(minutes=1)
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud", remaining_requests=0, limit_requests=10, reset_at=reset))

    result = QuotaAwareScheduler(registry).decide("cloud", now=now)

    assert result.action == "refresh"


def test_unknown_quota_is_not_treated_as_exhausted():
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud"))

    result = QuotaAwareScheduler(registry).decide("cloud")

    assert result.action == "eligible"
