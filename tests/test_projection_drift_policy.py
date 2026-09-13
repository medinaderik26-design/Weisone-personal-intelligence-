from types import SimpleNamespace
from core.projection_drift_policy import ProjectionDriftPolicy


def drift(changed, changes):
    return SimpleNamespace(changed=changed, changes=tuple(changes))


def test_no_drift_continues():
    decision = ProjectionDriftPolicy().classify(drift(False, ()))
    assert decision.classification == "no_drift"
    assert decision.action == "continue"


def test_stage_progression_is_expected():
    decision = ProjectionDriftPolicy().classify(drift(True, ("stages", "current_stage")))
    assert decision.classification == "expected_progression"
    assert decision.action == "continue"


def test_completion_evidence_progression_is_expected():
    decision = ProjectionDriftPolicy().classify(
        drift(True, ("stages", "current_stage", "evidence_complete"))
    )
    assert decision.classification == "expected_progression"
    assert decision.action == "continue"


def test_intent_change_requires_human_review():
    decision = ProjectionDriftPolicy().classify(drift(True, ("intent_id", "stages")))
    assert decision.classification == "identity_divergence"
    assert decision.action == "human_review"


def test_unknown_drift_requires_reinspection():
    decision = ProjectionDriftPolicy().classify(drift(True, ("evidence_complete",)))
    assert decision.classification == "unexpected_divergence"
    assert decision.action == "reinspect"
