from datetime import datetime, timezone

import pytest

from core.revocation import RevocationGuard, RevocationRegistry


def test_revocation_blocks_future_execution():
    registry = RevocationRegistry()
    registry.revoke("person", "cloud", "summary")
    result = RevocationGuard(registry).check("person", "cloud", "summary")
    assert result.allowed is False


def test_unrevoked_scope_remains_allowed():
    registry = RevocationRegistry()
    registry.revoke("person", "cloud", "summary")
    result = RevocationGuard(registry).check("person", "cloud", "coding")
    assert result.allowed is True


def test_revocation_preserves_reason_and_timestamp():
    now = datetime.now(timezone.utc)
    registry = RevocationRegistry()
    event = registry.revoke("person", "cloud", "summary", reason="user requested removal", now=now)
    assert event.reason == "user requested removal"
    assert event.revoked_at == now


def test_invalid_revocation_rejected():
    with pytest.raises(ValueError):
        RevocationRegistry().revoke("", "cloud", "summary")
