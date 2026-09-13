from datetime import datetime, timezone

from core.quota_adapter import QuotaAdapter, QuotaReport, StaticQuotaSource
from core.quota_window import QuotaRegistry


def test_adapter_records_explicit_quota_and_reset():
    reset = datetime(2026, 9, 13, 18, 0, tzinfo=timezone.utc)
    registry = QuotaRegistry()
    adapter = QuotaAdapter(
        StaticQuotaSource(
            QuotaReport(
                provider="cloud-sim",
                remaining_requests=7,
                limit_requests=10,
                reset_at=reset,
            )
        ),
        registry,
    )

    window = adapter.refresh()

    assert window.remaining_requests == 7
    assert window.limit_requests == 10
    assert window.reset_at == reset
    assert registry.get("cloud-sim") == window


def test_unknown_quota_remains_unknown():
    registry = QuotaRegistry()
    adapter = QuotaAdapter(
        StaticQuotaSource(QuotaReport(provider="cloud-sim")),
        registry,
    )

    window = adapter.refresh()

    assert window.known is False
    assert window.exhausted is False
    assert registry.can_execute("cloud-sim") is True
