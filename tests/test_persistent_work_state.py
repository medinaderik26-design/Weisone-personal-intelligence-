import pytest

from core.persistent_work_state import InMemoryWorkStateStore, WorkState


def test_work_state_survives_store_operations():
    store = InMemoryWorkStateStore()
    state = WorkState(task_id="t1", status="running", attempt_count=1, provider="local")
    store.save(state)

    recovered = store.get("t1")
    assert recovered is not None
    assert recovered.status == "running"
    assert recovered.attempt_count == 1
    assert recovered.provider == "local"


def test_invalid_state_rejected():
    with pytest.raises(ValueError):
        WorkState(task_id="t1", status="unknown").validate()


def test_empty_task_id_rejected():
    with pytest.raises(ValueError):
        WorkState(task_id="").validate()
