from core.v01_execution_slice import PersonalIntelligenceSlice, StubProvider

def test_ci_smoke_same_work_id():
    result = PersonalIntelligenceSlice(StubProvider()).execute("ci-work-003", "ci-smoke")
    assert result.evidence.work_id == "ci-work-003"
    assert result.continuity.open_work_ids == []
