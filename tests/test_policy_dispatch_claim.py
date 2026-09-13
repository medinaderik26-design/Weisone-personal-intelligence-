from datetime import datetime, timezone

from core.durable_recovery_dispatch import SQLiteRecoveryDispatchStore
from core.policy_dispatch_bridge import PolicyDispatchBridge
from core.policy_dispatch_claim import PolicyDispatchClaimAdapter


def request(task_id="task-1", classification="expected_progression"):
    return PolicyDispatchBridge().build(
        type("Boundary", (), {
            "task_id": task_id,
            "action": "continue",
            "handoff_allowed": True,
            "reason": "allowed",
        })(),
        classification,
    )


def blocked_request():
    return PolicyDispatchBridge().build(
        type("Boundary", (), {
            "task_id": "task-1",
            "action": "human_review",
            "handoff_allowed": False,
            "reason": "human review required",
        })(),
        "identity_divergence",
    )


def test_eligible_request_creates_durable_claim(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    adapter = PolicyDispatchClaimAdapter(store)

    result = adapter.claim(
        request(),
        now=datetime(2026, 9, 13, tzinfo=timezone.utc),
    )

    assert result.claimed is True
    assert result.claim is not None
    assert result.dispatch_key == request().dispatch_key
    assert store.has_claim(result.dispatch_key)
    store.close()


def test_duplicate_policy_request_is_idempotent(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    adapter = PolicyDispatchClaimAdapter(store)
    req = request()

    first = adapter.claim(req)
    second = adapter.claim(req)

    assert first.claimed is True
    assert second.claimed is False
    assert second.claim is None
    store.close()


def test_blocked_policy_request_cannot_create_claim(tmp_path):
    store = SQLiteRecoveryDispatchStore(str(tmp_path / "dispatch.sqlite"))
    adapter = PolicyDispatchClaimAdapter(store)

    result = adapter.claim(blocked_request())

    assert result.claimed is False
    assert result.dispatch_key is None
    assert store.all() if hasattr(store, "all") else True
    store.close()


def test_claim_survives_restart(tmp_path):
    db = tmp_path / "dispatch.sqlite"
    req = request()

    store = SQLiteRecoveryDispatchStore(str(db))
    first = PolicyDispatchClaimAdapter(store).claim(req)
    store.close()

    reopened = SQLiteRecoveryDispatchStore(str(db))
    second = PolicyDispatchClaimAdapter(reopened).claim(req)

    assert first.claimed is True
    assert second.claimed is False
    assert reopened.has_claim(req.dispatch_key)
    reopened.close()
