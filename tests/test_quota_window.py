from datetime import datetime, timezone

import pytest

from core.quota_window import QuotaRegistry, QuotaWindow


def test_quota_window_accepts_known_capacity_and_reset():
    window = QuotaWindow(
        provider="cloud-a",
        remaining_requests=7,
        limit_requests=10,
        reset_at=datetime(2026, 9, 13, 15, 0, tzinfo=timezone.utc),
    )

    window.validate()

    assert window.known is True
    assert window.exhausted is False


def test_exhausted_window_blocks_execution():
    registry = QuotaRegistry()
    registry.record(QuotaWindow(provider="cloud-a", remaining_requests=0))

    assert registry.can_execute("cloud-a") is False


def test_unknown_quota_does_not_block_by_assumption():
    registry = QuotaRegistry()

    assert registry.can_execute("cloud-a") is True


def test_remaining_requests_cannot_exceed_limit():
    window = QuotaWindow(provider="cloud-a", remaining_requests=11, limit_requests=10)

    with pytest.raises(ValueError, match="cannot exceed"):
        window.validate()
