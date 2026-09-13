from core.lifecycle_projection import LifecycleProjection
from core.projection_drift import ProjectionDriftDetector


def projection(stages, complete=False):
    return LifecycleProjection("t1", "i1", tuple(stages), stages[-1] if stages else None, complete)


def test_identical_projections_have_no_drift():
    result = ProjectionDriftDetector().compare(projection(("authorized",)), projection(("authorized",)))
    assert result.changed is False
    assert result.changes == ()


def test_stage_progression_is_described_not_judged():
    result = ProjectionDriftDetector().compare(
        projection(("authorized",)),
        projection(("authorized", "handed_off")),
    )
    assert result.changed is True
    assert result.changes == ("stages", "current_stage")


def test_identity_change_is_explicit():
    result = ProjectionDriftDetector().compare(
        projection(("authorized",)),
        LifecycleProjection("t1", "i2", ("authorized",), "authorized", False),
    )
    assert result.changes == ("intent_id",)
