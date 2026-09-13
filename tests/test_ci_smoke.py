from core.v01_execution_slice import PersonalIntelligenceSlice, StubProvider


def test_ci_executes_the_v01_slice():
    result = PersonalIntelligenceSlice(StubProvider()).execute("ci-work-001", "ci-smoke")
    assert result.proposal.status == "accepted"
    assert result.run is not None and result.run.success
    assert result.evidence is not None and result.evidence.verified
    assert result.evidence.work_id == "ci-work-001"
    assert result.continuity.open_work_ids == []
