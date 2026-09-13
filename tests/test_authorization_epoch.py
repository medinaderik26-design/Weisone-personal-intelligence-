from core.authorization_epoch import AuthorizationEpochGuard, AuthorizationEpochRegistry


def test_new_scope_starts_at_epoch_zero():
    registry = AuthorizationEpochRegistry()
    assert registry.current("person", "cloud", "summary") == 0


def test_advance_creates_monotonic_epoch():
    registry = AuthorizationEpochRegistry()
    first = registry.advance("person", "cloud", "summary")
    second = registry.advance("person", "cloud", "summary")
    assert first.version == 1
    assert second.version == 2


def test_current_epoch_is_valid():
    registry = AuthorizationEpochRegistry()
    epoch = registry.advance("person", "cloud", "summary")
    assert AuthorizationEpochGuard(registry).check(epoch).current is True


def test_old_epoch_becomes_stale_after_advance():
    registry = AuthorizationEpochRegistry()
    old = registry.advance("person", "cloud", "summary")
    registry.advance("person", "cloud", "summary")
    result = AuthorizationEpochGuard(registry).check(old)
    assert result.current is False
    assert result.reason == "authorization decision is stale"


def test_epochs_are_scoped():
    registry = AuthorizationEpochRegistry()
    cloud = registry.advance("person", "cloud", "summary")
    local = registry.advance("person", "local", "summary")
    assert cloud.version == 1
    assert local.version == 1
