from datetime import datetime, timedelta, timezone

import pytest

from core.consent import ConsentRegistry


def test_consent_must_be_explicit():
    registry = ConsentRegistry()
    assert registry.permits("person", "cloud", "summary") is False


def test_grant_allows_matching_provider_and_task():
    registry = ConsentRegistry()
    registry.grant("person", "cloud", "summary")
    assert registry.permits("person", "cloud", "summary") is True
    assert registry.permits("person", "cloud", "coding") is False
    assert registry.permits("person", "other", "summary") is False


def test_revoke_removes_consent():
    registry = ConsentRegistry()
    registry.grant("person", "cloud", "summary")
    registry.revoke("person", "cloud", "summary")
    assert registry.permits("person", "cloud", "summary") is False


def test_expired_consent_is_not_active():
    registry = ConsentRegistry()
    now = datetime.now(timezone.utc)
    registry.grant("person", "cloud", "summary", expires_at=now + timedelta(seconds=1), now=now)
    assert registry.permits("person", "cloud", "summary", now=now + timedelta(seconds=2)) is False


def test_invalid_grant_rejected():
    with pytest.raises(ValueError):
        ConsentRegistry().grant("", "cloud", "summary")
