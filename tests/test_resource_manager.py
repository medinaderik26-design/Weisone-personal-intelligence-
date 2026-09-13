from core.resource_manager import ResourceManager


def test_request_budget_is_enforced():
    manager = ResourceManager()
    manager.register_provider("local", requests_limit=2)

    assert manager.can_request("local") is True
    manager.record_request("local", input_tokens=10, output_tokens=5)
    assert manager.can_request("local") is True
    manager.record_request("local", input_tokens=8, output_tokens=4)

    assert manager.can_request("local") is False
    snapshot = manager.snapshot("local")
    assert snapshot.requests_used == 2
    assert snapshot.requests_remaining == 0
    assert snapshot.input_tokens == 18
    assert snapshot.output_tokens == 9


def test_unknown_provider_is_denied():
    manager = ResourceManager()
    assert manager.can_request("unknown") is False


def test_failure_and_cost_are_recorded():
    manager = ResourceManager()
    manager.register_provider("cloud")
    manager.record_request(
        "cloud",
        estimated_cost=0.02,
        failed=True,
    )

    snapshot = manager.snapshot("cloud")
    assert snapshot.failures == 1
    assert snapshot.estimated_cost == 0.02
