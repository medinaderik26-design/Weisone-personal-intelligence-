from core.durable_recovery_dispatch import SQLiteRecoveryDispatchStore


def test_dispatch_claim_survives_reopen(tmp_path):
    path = tmp_path / "dispatch.db"
    first = SQLiteRecoveryDispatchStore(str(path))
    claim = first.claim("task-1", "recoverable_divergence", "reinspect")
    assert claim is not None
    first.close()

    second = SQLiteRecoveryDispatchStore(str(path))
    duplicate = second.claim("task-1", "recoverable_divergence", "reinspect")
    assert duplicate is None
    assert second.has_claim(claim.dispatch_key)
    second.close()


def test_different_action_gets_different_key(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.db"))
    first = store.claim("task-1", "recoverable_divergence", "reinspect")
    second = store.claim("task-1", "human_review_required", "human_review")
    store.close()
    assert first is not None
    assert second is not None
    assert first.dispatch_key != second.dispatch_key
