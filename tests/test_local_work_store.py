from core.local_work_store import SQLiteWorkStateStore
from core.persistent_work_state import WorkState


def test_sqlite_store_round_trip(tmp_path):
    db = tmp_path / "work.db"
    store = SQLiteWorkStateStore(str(db))
    store.save(WorkState(task_id="task-1", status="running", attempt_count=2, provider="local"))
    store.close()

    recovered_store = SQLiteWorkStateStore(str(db))
    recovered = recovered_store.get("task-1")
    assert recovered is not None
    assert recovered.status == "running"
    assert recovered.attempt_count == 2
    assert recovered.provider == "local"
    recovered_store.close()


def test_unfinished_returns_queued_and_running(tmp_path):
    store = SQLiteWorkStateStore(str(tmp_path / "work.db"))
    store.save(WorkState(task_id="queued", status="queued"))
    store.save(WorkState(task_id="running", status="running"))
    store.save(WorkState(task_id="done", status="completed"))

    ids = {state.task_id for state in store.unfinished()}
    assert ids == {"queued", "running"}
    store.close()
