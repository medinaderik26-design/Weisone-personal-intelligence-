from core.durable_lifecycle_projection import SQLiteLifecycleProjectionStore
from core.lifecycle_projection import LifecycleProjection


def projection(task_id, stages):
    return LifecycleProjection(
        task_id=task_id,
        intent_id="intent-1",
        stages=tuple(stages),
        current_stage=stages[-1] if stages else None,
        evidence_complete=stages[-1:] == ("externally_confirmed",),
    )


def test_projection_versions_survive_restart(tmp_path):
    db = tmp_path / "lifecycle.sqlite"
    store = SQLiteLifecycleProjectionStore(str(db))
    assert store.save(projection("task-1", ["authorized"])) == 1
    assert store.save(projection("task-1", ["authorized", "handed_off"])) == 2
    store.close()

    reopened = SQLiteLifecycleProjectionStore(str(db))
    assert reopened.versions("task-1") == (1, 2)
    assert '"current_stage": "handed_off"' in reopened.latest_json("task-1")
    reopened.close()


def test_tasks_have_independent_versions(tmp_path):
    store = SQLiteLifecycleProjectionStore(str(tmp_path / "lifecycle.sqlite"))
    assert store.save(projection("task-1", ["authorized"])) == 1
    assert store.save(projection("task-2", ["authorized"])) == 1
    assert store.versions("task-1") == (1,)
    assert store.versions("task-2") == (1,)
    store.close()
