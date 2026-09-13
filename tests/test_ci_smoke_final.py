from core.v01_execution_slice import PersonalIntelligenceSlice, StubProvider

def test_ci_smoke_final():
    result = PersonalIntelligenceSlice(StubProvider()).execute("ci-work-final", "ci-smoke")
    assert result.evidence is not None
    assert result.evidence.work_id == "ci-work-final"
    assert result.continuity.open_work_ids == []
