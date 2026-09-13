from core.v01_execution_slice import PersonalIntelligenceSlice, StubProvider

def test_ci_smoke():
    result = PersonalIntelligenceSlice(StubProvider()).execute("ci-work-002", "ci-smoke")
    assert result.evidence.verified
